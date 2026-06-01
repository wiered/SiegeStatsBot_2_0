import asyncio
import logging
from typing import Any, Protocol, TypeVar

import aiohttp
from pydantic import BaseModel, ValidationError

from config import Config
from core.parser.cache import RedisJsonCache, make_r6data_cache_key
from core.parser.models import (
    AccountInfoResponse,
    SeasonalStatsResponse,
    StatsResponse,
)
from core.parser.r6data_mapper import map_account_info_to_profile, map_player
from core.player_data_models import NormalizedPlayerData, NormalizedProfile


logger = logging.getLogger(__name__)
R6DataResponse = TypeVar("R6DataResponse", bound=BaseModel)


class JsonCache(Protocol):
    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def get_json(self, key: str) -> dict[str, Any] | None: ...

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None: ...


class Parser:
    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 15,
        cache: JsonCache | None = None,
    ):
        self.__r6data_api_url = "https://api.r6data.com/api/stats"
        self.__timeout = timeout
        config = Config()
        self.__api_key = api_key if api_key is not None else config.r6data_api_key
        self.__session: aiohttp.ClientSession | None = None
        self.__cache = cache
        self.__owns_cache = False
        self.__redis_url = config.redis_url
        self.__redis_cache_ttl_seconds = config.redis_cache_ttl_seconds
        self.__redis_enabled = config.redis_enabled

    async def __aenter__(self) -> "Parser":
        timeout = aiohttp.ClientTimeout(total=self.__timeout)
        self.__session = aiohttp.ClientSession(
            headers={"api-key": self.__api_key},
            timeout=timeout,
        )
        if self.__cache is None and self.__redis_enabled:
            self.__cache = RedisJsonCache(
                self.__redis_url,
                self.__redis_cache_ttl_seconds,
            )
            self.__owns_cache = True
        if self.__cache is not None:
            await self.__cache.connect()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if self.__session is not None:
            await self.__session.close()
            self.__session = None
        if self.__cache is not None and self.__owns_cache:
            await self.__cache.close()
            self.__cache = None
            self.__owns_cache = False

    async def get_account_info(self, username: str, platform: str = "uplay") -> dict:
        return await self.__get_r6data_json(
            {
                "type": "accountInfo",
                "nameOnPlatform": username,
                "platformType": platform,
            }
        )

    async def get_stats(
        self,
        username: str,
        platform: str = "uplay",
        platform_family: str = "pc",
    ) -> dict:
        return await self.__get_r6data_json(
            {
                "type": "stats",
                "nameOnPlatform": username,
                "platformType": platform,
                "platform_families": platform_family,
            }
        )

    async def get_seasonal_stats(self, username: str, platform: str = "uplay") -> dict:
        return await self.__get_r6data_json(
            {
                "type": "seasonalStats",
                "nameOnPlatform": username,
                "platformType": platform,
            }
        )

    async def get_account_profile(
        self,
        username: str,
        platform: str = "uplay",
    ) -> NormalizedProfile | None:
        account_info = self.__validate_or_default(
            AccountInfoResponse,
            await self.get_account_info(username, platform),
            {},
        )
        if not account_info.profiles:
            return None
        return map_account_info_to_profile(account_info, username, platform)

    async def get_seasons_stats2(self, username: str, platform: str = "uplay") -> dict:
        return await self.__get_r6data_json(
            {
                "type": "seasonsStats",
                "nameOnPlatform": username,
                "platformType": platform,
            }
        )

    async def get_seasons_stats(self, username: str, platform: str = "uplay") -> dict:
        return await self.__get_r6data_json(
            {
                "type": "seasonsStats",
                "nameOnPlatform": username,
                "platformType": platform,
            }
        )

    async def parse_player(self, username: str) -> NormalizedPlayerData:
        account_info_data, stats_data, seasonal_stats_data = await asyncio.gather(
            self.get_account_info(username),
            self.get_stats(username),
            self.get_seasonal_stats(username),
        )
        seasons_stats_data = await self.get_seasons_stats(username)
        account_info = self.__validate_or_default(
            AccountInfoResponse,
            account_info_data,
            {},
        )
        stats = self.__validate_or_default(
            StatsResponse,
            stats_data,
            {"data": {}},
        )
        seasonal_stats = self.__validate_or_default(
            SeasonalStatsResponse,
            seasonal_stats_data,
            {"data": {}},
        )
        seasons_stats = self.__validate_or_default(
            StatsResponse, seasons_stats_data, {"data": {}}
        )

        return map_player(
            account_info=account_info,
            stats=stats,
            seasonal_stats=seasonal_stats,
            username=username,
            seasons=seasons_stats,
        )

    async def __get_r6data_json(self, params: dict[str, str]) -> dict:
        if self.__session is None:
            msg = "Parser must be used as an async context manager"
            raise RuntimeError(msg)

        response_type = params.get("type", "unknown")
        cache_key = make_r6data_cache_key(params)
        if self.__cache is not None:
            cached_data = await self.__cache.get_json(cache_key)
            if cached_data is not None:
                logger.debug("R6Data cache hit for %s", response_type)
                return cached_data
            logger.debug("R6Data cache miss for %s", response_type)

        try:
            async with self.__session.get(
                self.__r6data_api_url,
                params=params,
            ) as response:
                if response.status != 200:
                    logger.warning(
                        "R6Data request returned status %s for %s",
                        response.status,
                        response_type,
                    )
                    return {}

                try:
                    data = await response.json()
                except (aiohttp.ContentTypeError, ValueError):
                    logger.warning("R6Data returned invalid JSON for %s", response_type)
                    return {}
        except aiohttp.ClientError:
            logger.exception("R6Data request failed: %s", response_type)
            return {}

        if not isinstance(data, dict):
            return {}

        if self.__cache is not None:
            await self.__cache.set_json(
                cache_key,
                data,
                ttl_seconds=self.__redis_cache_ttl_seconds,
            )
            logger.debug("R6Data cache set for %s", response_type)

        return data

    def __validate_or_default(
        self,
        model: type[R6DataResponse],
        data: dict[str, Any],
        default_data: dict[str, Any],
    ) -> R6DataResponse:
        try:
            return model.model_validate(data)
        except ValidationError:
            logger.exception("Invalid R6Data %s payload", model.__name__)
            return model.model_validate(default_data)
