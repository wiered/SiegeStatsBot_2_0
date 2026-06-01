import logging
from typing import Any, TypeVar

import requests
from pydantic import BaseModel, ValidationError

from config import Config
from core.parser.models import (
    AccountInfoResponse,
    SeasonalStatsResponse,
    StatsResponse,
)
from core.parser.r6data_mapper import map_account_info_to_profile, map_player
from core.player_data_models import NormalizedPlayerData, NormalizedProfile


logger = logging.getLogger(__name__)
R6DataResponse = TypeVar("R6DataResponse", bound=BaseModel)


class Parser(requests.Session):
    def __init__(self, api_key: str | None = None, timeout: int = 15):
        super().__init__()
        self.__r6data_api_url = "https://api.r6data.com/api/stats"
        self.__timeout = timeout
        self.__api_key = api_key if api_key is not None else Config().r6data_api_key
        self.headers.update({"api-key": self.__api_key})

    def get_account_info(self, username: str, platform: str = "uplay") -> dict:
        return self.__get_r6data_json(
            {
                "type": "accountInfo",
                "nameOnPlatform": username,
                "platformType": platform,
            }
        )

    def get_stats(
        self,
        username: str,
        platform: str = "uplay",
        platform_family: str = "pc",
    ) -> dict:
        return self.__get_r6data_json(
            {
                "type": "stats",
                "nameOnPlatform": username,
                "platformType": platform,
                "platform_families": platform_family,
            }
        )

    def get_seasonal_stats(self, username: str, platform: str = "uplay") -> dict:
        return self.__get_r6data_json(
            {
                "type": "seasonalStats",
                "nameOnPlatform": username,
                "platformType": platform,
            }
        )

    def get_account_profile(
        self,
        username: str,
        platform: str = "uplay",
    ) -> NormalizedProfile | None:
        account_info = self.__validate_or_default(
            AccountInfoResponse,
            self.get_account_info(username, platform),
            {},
        )
        if not account_info.profiles:
            return None
        return map_account_info_to_profile(account_info, username, platform)

    def parse_player(self, username: str) -> NormalizedPlayerData:
        account_info = self.__validate_or_default(
            AccountInfoResponse,
            self.get_account_info(username),
            {},
        )
        stats = self.__validate_or_default(
            StatsResponse,
            self.get_stats(username),
            {"data": {}},
        )
        seasonal_stats = self.__validate_or_default(
            SeasonalStatsResponse,
            self.get_seasonal_stats(username),
            {"data": {}},
        )

        return map_player(
            account_info=account_info,
            stats=stats,
            seasonal_stats=seasonal_stats,
            username=username,
        )

    def __get_r6data_json(self, params: dict[str, str]) -> dict:
        response_type = params.get("type", "unknown")
        try:
            response = self.get(
                self.__r6data_api_url,
                params=params,
                timeout=self.__timeout,
            )
        except requests.RequestException:
            logger.exception("R6Data request failed: %s", response_type)
            return {}

        if response.status_code != 200:
            logger.warning(
                "R6Data request returned status %s for %s",
                response.status_code,
                response_type,
            )
            return {}

        try:
            data = response.json()
        except ValueError:
            logger.warning("R6Data returned invalid JSON for %s", response_type)
            return {}

        return data if isinstance(data, dict) else {}

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
