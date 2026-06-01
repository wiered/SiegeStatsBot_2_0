import os


def _get_env_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _get_env_int(name: str, default: int = 0) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    return int(value)


def _get_env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    _token: str = ""
    _log_level: str = ""
    _guild_id: int = 0
    _r6data_api_key: str = ""
    _redis_url: str = "redis://localhost:6379/0"
    _redis_cache_ttl_seconds: int = 900
    _redis_enabled: bool = True

    def __init__(self):
        self.read_config()

    @property
    def token(self):
        return self._token

    @property
    def log_level(self):
        return self._log_level

    @property
    def guild_id(self):
        return self._guild_id

    @property
    def r6data_api_key(self):
        return self._r6data_api_key

    @property
    def redis_url(self):
        return self._redis_url

    @property
    def redis_cache_ttl_seconds(self):
        return self._redis_cache_ttl_seconds

    @property
    def redis_enabled(self):
        return self._redis_enabled

    def read_config(self):
        self._token = _get_env_str("TOKEN")
        self._log_level = _get_env_str("LOG_LEVEL", "INFO")
        self._guild_id = _get_env_int("GUILD_ID")
        self._r6data_api_key = _get_env_str(
            "R6DATA_API_KEY",
            default=_get_env_str("R6DATA_TOKEN"),
        )
        self._redis_url = _get_env_str("REDIS_URL", "redis://localhost:6379/0")
        self._redis_cache_ttl_seconds = _get_env_int(
            "REDIS_CACHE_TTL_SECONDS",
            default=900,
        )
        self._redis_enabled = _get_env_bool("REDIS_ENABLED", default=True)

    def read_roles(self):
        self.unranked = _get_env_int("ROLE_UNRANKED")
        self.copper = _get_env_int("ROLE_COPPER")
        self.bronze = _get_env_int("ROLE_BRONZE")
        self.silver = _get_env_int("ROLE_SILVER")
        self.gold = _get_env_int("ROLE_GOLD")
        self.platinum = _get_env_int("ROLE_PLATINUM")
        self.emerald = _get_env_int("ROLE_EMERALD")
        self.diamond = _get_env_int("ROLE_DIAMOND")
        self.champion = _get_env_int("ROLE_CHAMPION")
