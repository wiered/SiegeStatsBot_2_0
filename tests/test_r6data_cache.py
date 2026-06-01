import asyncio
from typing import Any


from core.parser import Parser
from core.parser.cache import make_r6data_cache_key


class FakeCache:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}
        self.get_calls = 0
        self.set_calls = 0
        self.ttl_seconds: int | None = None

    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def get_json(self, key: str) -> dict[str, Any] | None:
        self.get_calls += 1
        return self.values.get(key)

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        self.set_calls += 1
        self.ttl_seconds = ttl_seconds
        self.values[key] = value


class FakeResponse:
    def __init__(
        self,
        status: int = 200,
        payload: Any = None,
        json_exc: Exception | None = None,
    ) -> None:
        self.status = status
        self.payload = payload if payload is not None else {"ok": True}
        self.json_exc = json_exc

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        return None

    async def json(self) -> Any:
        if self.json_exc is not None:
            raise self.json_exc
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.get_calls = 0

    def get(self, *_args: object, **_kwargs: object) -> FakeResponse:
        self.get_calls += 1
        return self.response

    async def close(self) -> None:
        return None


def run_parser_request(
    cache: FakeCache,
    response: FakeResponse,
) -> tuple[dict[str, Any], FakeSession]:
    async def request() -> tuple[dict[str, Any], FakeSession]:
        parser = Parser(api_key="", cache=cache)
        await parser.__aenter__()
        session = FakeSession(response)
        setattr(parser, "_Parser__session", session)
        data = await parser.get_account_info("Pollz")
        await parser.__aexit__()
        return data, session

    return asyncio.run(request())


def test_r6data_cache_key_is_stable() -> None:
    params = {
        "type": "stats",
        "nameOnPlatform": " Pollz ",
        "platformType": "UPLAY",
        "platform_families": "pc",
    }
    reordered_params = {
        "platform_families": "pc",
        "platformType": "UPLAY",
        "nameOnPlatform": " Pollz ",
        "type": "stats",
    }

    assert make_r6data_cache_key(params) == make_r6data_cache_key(reordered_params)


def test_r6data_cache_key_separates_request_types() -> None:
    common_params = {
        "nameOnPlatform": "pollz",
        "platformType": "uplay",
    }

    seasonal_key = make_r6data_cache_key({**common_params, "type": "seasonalStats"})
    seasons_key = make_r6data_cache_key({**common_params, "type": "seasonsStats"})

    assert seasonal_key != seasons_key


def test_parser_uses_cached_r6data_response() -> None:
    cache = FakeCache()
    key = make_r6data_cache_key(
        {
            "type": "accountInfo",
            "nameOnPlatform": "Pollz",
            "platformType": "uplay",
        }
    )
    cache.values[key] = {"cached": True}

    data, session = run_parser_request(cache, FakeResponse(payload={"live": True}))

    assert data == {"cached": True}
    assert cache.get_calls == 1
    assert cache.set_calls == 0
    assert session.get_calls == 0


def test_parser_stores_successful_r6data_response() -> None:
    cache = FakeCache()

    data, session = run_parser_request(cache, FakeResponse(payload={"live": True}))

    assert data == {"live": True}
    assert session.get_calls == 1
    assert cache.get_calls == 1
    assert cache.set_calls == 1
    assert cache.ttl_seconds == 900


def test_parser_does_not_cache_non_200_response() -> None:
    cache = FakeCache()

    data, session = run_parser_request(cache, FakeResponse(status=500))

    assert data == {}
    assert session.get_calls == 1
    assert cache.get_calls == 1
    assert cache.set_calls == 0


def test_parser_does_not_cache_invalid_json() -> None:
    cache = FakeCache()

    data, session = run_parser_request(
        cache,
        FakeResponse(json_exc=ValueError("invalid json")),
    )

    assert data == {}
    assert session.get_calls == 1
    assert cache.get_calls == 1
    assert cache.set_calls == 0


def test_parser_does_not_cache_non_dict_json() -> None:
    cache = FakeCache()

    data, session = run_parser_request(cache, FakeResponse(payload=[]))

    assert data == {}
    assert session.get_calls == 1
    assert cache.get_calls == 1
    assert cache.set_calls == 0
