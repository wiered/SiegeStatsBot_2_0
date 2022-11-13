import requests


from core import json_unpacker
from core.data import APIUrls



class Parser(requests.Session):
    def __init__(self):
        # API - tabstats API - https://r6.apitab.net/website
        # init super class
        super().__init__()
        
        # payload
        self.__payload = {"display_name": "User", "platform": "uplay"}
        

    def parse_player(
        self, 
        player: str, 
        _id: bool = False, 
        full: bool = False
    ) -> dict:
        """_summary_: Search player by name or id

        Args:
            player (str): Rainbow Six Siege player name or id
            _id (bool, optional): if True, will search player buy his id. Defaults to False.
            full (bool, optional): if True, return overall player data. Defaults to False.

        Returns:
            list or str or dict: 'list of players' or 'player id' or 'player data'
        """
        
        if _id:
            if full:
                return self.__parse_full_json__(player)
            return self.__parse_by_id__(player)
        if full:
            return self.__parse_full_json__(self.parse_id(player))
        return self.__find_player__(player)
    
                      
    def search_player(self, player) -> list:
        return self.__search_player_by_name__(player)
        
        
    def __search_player_by_name__(self, playername: str) -> list:
        """_summary_ : Search player by name

        Args:
            playername (str): Rainbow Six Siege player name

        Returns:
            list: list of parsed players
        """
        
        self.__payload["display_name"] = playername
        response = self.get(APIUrls.tabstats_search_api_url, params=self.__payload)
        if response.status_code != 200:
            return []
        return [json_unpacker.unpack_json(_json) for _json in response.json()]
    
    
    def __find_player__(self, playername: str) -> dict:
        """_summary_ : Find player by name
        
        Args:
            playername (str): Rainbow Six Siege player name
            
        Returns:
            dict: parsed player data (first player in search results)
        """
        
        player = self.__search_player_by_name__(playername)
        if not player:
            return {}
        return player[0]
    
    
    def parse_id(self, playername: str) -> str:
        """_summary_ : Parse player id from player name

        Args:
            playername (str): Rainbow Six Siege player name

        Returns:
            str: Rainbow Six Siege player id
        """
        
        response = self.__find_player__(playername)
        if not response:
            return ""
        return response["id"]
    
    
    def __parse_full_json__(self, playerid: str) -> dict:
        """_summary_ : Parse overall player data from player id

        Args:
            playerid (str): Rainbow Six Siege player id

        Returns:
            dict: overall player data in json format
        """
        
        response = self.get(APIUrls.tabstats_profie_api_url.format(playerid))
        if response.status_code != 200:
            return {}
        
        return response.json()
    
    
    def __parse_by_id__(self, playerid: str) -> dict:
        """_summary_ : Parse player data from player id

        Args:
            playerid (str): Rainbow Six Siege player id

        Returns:
            dict: short player data in dict
        """

        response = self.__parse_full_json__(playerid)
        if not response:
            return {}
        
        return json_unpacker.unpack_json(response, full=True)
    
    
    
