import configparser
import os


class Config:
    _token: str = ""
    _log_level: str = ""
    _guild_id: int = 0
    
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

    def read_config(self):
        with open("./config/config.ini", "r") as config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)
            self._token = config.get('DEFAULT', 'token')
            self._log_level = config.get('DEFAULT', 'log_level')
            self._guild_id = int(config.get('DEFAULT', 'guild_id'))
