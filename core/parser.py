import requests

class Parser(requests.Session):
    def __init__(self):
        # API - tabstats API - https://r6.apitab.net/website
        
        # API Links
        self.__tabstats_search_api_url = "https://r6.apitab.net/website/search"
        self.__tabstats_profie_api_url = "https://r6.apitab.net/website/profiles/{}"
        
        # init super class
        super().__init__()
        
        # API payload
        self.__payload = {"display_name": "User", "platform": "uplay"}
          
    
    def search_player(self, playername: str) -> list:
        """_summary_ : Search player by name

        Args:
            playername (str): Rainbow Six Siege player name

        Returns:
            list: list of parsed players
        """
        
        self.__payload["display_name"] = playername
        response = self.get(self.__tabstats_search_api_url, params=self.__payload)
        if response.status_code != 200:
            return []
        return [self.__unpack_json__(_json) for _json in response.json()]

    
    def parse_player(self, player_id: str) -> dict:
        """_summary_ : Parse overall player data from player id

        Args:
            playerid (str): Rainbow Six Siege player id

        Returns:
            dict: overall player data in json format
        """
        
        response = self.get(self.__tabstats_profie_api_url.format(player_id))
        if response.status_code != 200:
            return {}
        
        return response.json()


    def __default_search_json__(self) -> dict:
        return {
            "name": "N/A",
            "id": "N/A",
            "level": "N/A",
            "rank": "N/A",
        }


    def __extract_rank__(self, response, _json) -> dict:
        rank = None
        cssr = response.get("current_season_ranked_record")
        if cssr:
            rank = cssr.get("rank_slug")[3:]
            
        if rank:
            _json.update({"rank": rank})
            
        return _json


    def __extract_profile__(self, _json: dict, response: dict) -> dict:
        profile = response.get("profile")
        if profile:
            _json.update({"name": profile.get("display_name")})
            _json.update({"id": profile.get("user_id")})
            _json.update({"level": profile.get("level")})
        
        return _json


    def __unpack_json__(self, response, full=False) -> dict:
        """Unpack json from api to dict

        Args:
            response (_type_): raw json from api
            full (bool, optional): if true, unpacking from full json. Defaults to False.

        Returns:
            dict: unpacked json with player data
        """

        if not response:
            return {}

        _json = self.__default_search_json__()
        _json = self.__extract_profile__(_json, response)
        _json = self.__extract_rank__(response, _json)

        return _json