import logging


from core import csv_addon, parser
from core import type_helpers, json_unpacker


class UsersVault:    
    def __init__(self):
        self.__users = {}
    
    
    @property
    def users(self):
        return self.__users
    
    
    @property
    def keys(self):
        return self.__users.keys()
    
    
    def add_user(self, user):
        """_summary_: Add user to UsersVault

        Args:
            user (User): User object
        """        
        
        self.__users.update({int(user.d_id): user})
    
        
    def load_instance_from_csv(self):
        """_summary_: Instantiate UsersVault from csv

        Raises:
            FileNotFoundError: if csv file not found
        """        

        self.__users.clear()
        logging.info("Instantiating from csv")
        try:
            self.__load_users()
            logging.info("Users loaded")
        except FileNotFoundError:
            logging.exception("No such file or directory: './db/stats.csv'")
            raise FileNotFoundError(
                "[Errno 2] No such file or directory: './db/stats.csv'"
            )
    
    
    def __load_users(self):
        """_summary_: Load all authorized users from csv
        """        
        
        items = csv_addon.load_from_csv("./db/users.csv")
        if len(items) == 0:
            logging.warning("No users in csv")
            return
        for item in items:
            self.add_user(
                User(
                    name=str(item.get("name")),
                    siege_id=str(item.get("siege_id")),
                    d_id=type_helpers.get_d_id(item),
                    rank=str(item.get("rank")),
                )
            )
        logging.info("Users loaded from csv")
            
            
    def save_instance_to_csv(self):
        """_summary_: Save all authorized users to csv"""        

        print(*self.__users.values(), sep="\n")
        users_data = []
        for user in self.__users.values():
            users_data.append(json_unpacker.generate_user_data(user))
        csv_addon.write_to_csv("./db/users.csv", users_data)
        logging.info("All userdata saved")

    
    def get_user(self, d_id: int):
        """_summary_: Get user by discord id

        Args:
            d_id (int): user's discord ID

        Returns:
            User: User object
        """
        
        return self.__users.get(d_id)
    
    
    def delete_by_dID(self, d_id: int):
        """_summary_: Delete user by his discord ID

        Args:
            d_id (int): user's discord ID
        """
        
        del self.__users[d_id]
    
    
    def is_authorized(self, d_id: int) -> bool:
        """_summary_: Check if user is authorized

        Args:
            d_id (int): user's discord ID

        Returns:
            bool: True if user is authorized, False otherwise
        """
        
        return self.__users.get(d_id) is not None
    
    
    
class User:
    def __init__(
        self, 
        name: str = "", 
        d_id: int = 0, 
        siege_id: str = "", 
        rank: str = "Unranked"
    ):
        self.__siege_name = name
        self.__d_id = d_id
        self.__siege_id = siege_id
        self.__rank = rank
        
        self.__json: dict = {}
        self.__full_json = {}
              
        if not siege_id:
            self.parse_data(by_name=True)
        else:
            self.parse_data(is_full=True)
            

    @property
    def name(self) -> str:
        return self.__siege_name


    @property
    def d_id(self) -> int:
        return self.__d_id


    @property
    def siege_id(self) -> str:
        return self.__siege_id


    @property
    def rank(self) -> str:
        return self.__rank
    
    
    @property
    def level(self):
        try:
            return self.__json.get("level")
        except KeyError:
            return "0"
            
        
    @property
    def _json(self) -> dict:
        if self.__json:
            return self.__json
        return {}
    

    @property
    def full_json(self) -> dict:
        if self.__full_json:
            return self.__full_json
        return {}
        

    def parse_data(self, by_name: bool = False, is_full: bool = False):
        """_summary_: Parsing data from tabstats

        Args:
            by_name (bool, optional): if True, parse by name. Defaults to False.
        """
        
        req = self.__siege_id
        if by_name:
            req = self.__siege_name
            
        with parser.Parser() as _parser:
            _json = _parser.parse_player(req, _id=True)
            if isinstance(_json, dict):
                self.__json = _json
                
        self.__rank         = type_helpers.get_rank_from_json(self.__json)
        self.__siege_name   = type_helpers.get_name_from_json(self.__json)
        
        if by_name:
            self.__siege_id = type_helpers.get_siege_id(self.__json)          
        if is_full:
            self.__full_json = _parser.parse_player(self.__siege_id, _id=True, full=True)
            
        logging.info(f"Stats parsed: {self.__rank}")
        

    
    def __repr__(self) -> str:
        return f"User({self.__siege_name}, {self.__d_id}, {self.__siege_id}, {self.__rank})"