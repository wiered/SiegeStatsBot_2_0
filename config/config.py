import configparser


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
        with open("./config/config.ini", "r") as config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)
            self._token = config.get("DEFAULT", "token")
            self._log_level = config.get("DEFAULT", "log_level")
            self._guild_id = int(config.get("DEFAULT", "guild_id"))
            self._r6data_api_key = config.get(
                "DEFAULT",
                "r6data_api_key",
                fallback=config.get("DEFAULT", "r6data_token", fallback=""),
            )
            self._redis_url = config.get(
                "REDIS",
                "redis_url",
                fallback="redis://localhost:6379/0",
            )
            self._redis_cache_ttl_seconds = config.getint(
                "REDIS",
                "redis_cache_ttl_seconds",
                fallback=900,
            )
            self._redis_enabled = config.getboolean(
                "REDIS",
                "redis_enabled",
                fallback=True,
            )

    def read_roles(self):
        with open("./config/config.ini", "r") as config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)
            self.unranked = int(config.get("ROLES", "Unranked"))
            self.copper = int(config.get("ROLES", "Copper"))
            self.bronze = int(config.get("ROLES", "Bronze"))
            self.silver = int(config.get("ROLES", "Silver"))
            self.gold = int(config.get("ROLES", "Gold"))
            self.platinum = int(config.get("ROLES", "Platinum"))
            self.emerald = int(config.get("ROLES", "Emerald"))
            self.diamond = int(config.get("ROLES", "Diamond"))
            self.champion = int(config.get("ROLES", "Champion"))
