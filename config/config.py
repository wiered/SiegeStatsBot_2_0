import configparser
import os

class Config:
    def __init__(self):
        self.read_config()

    @property
    def token(self):
        return self.__token
    
    
    @property
    def log_level(self):
        return self.__log_level
    
    
    def read_config(self):
        with open("./config/config.ini", "r") as config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)
            self.__token = config.get('DEFAULT', 'token')
            self.__log_level = config.get('DEFAULT', 'log_level')
            
    
    def get_config(self, _key: str, selection: str = 'DEFAULT'):
        if not os.path.exists("./config/config.ini"):
            return None
        with open("./config/config.ini", "r") as config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)
            return config.get(selection, _key)