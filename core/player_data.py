from datetime import datetime, date

from core.data import RoleDicts
from core import type_helpers as th

api_url = "https://r6.apitab.net/website/profiles/{}"
avatar_url = "https://ubisoft-avatars.akamaized.net/{}/default_146_146.png"
profile_url = "https://tabstats.com/siege/player/{}/{}"
rank_champion_api = "https://img-gen.apitab.com/{}"
        
my_git = "https://github.com/wiered"
rickroll_gif = "https://media0.giphy.com/media/Vuw9m5wXviFIQ/giphy.gif?cid=790b7611191d9020f3a9bc7c3488e8d0a936952cc68a1ce8&rid=giphy.gif&ct=g"        
        

class PastSeasonRankedRecords:
    def __init__(self, seasons) -> None:
        if not isinstance(seasons, list):
            self.seasons = []
            self.keys = []
            
            return
        
        self.seasons = [PastSeasonRankedRecords.Season(season) for season in seasons]
        self.keys = [record.season_slug for record in self.seasons]
    
    
    def __getitem__(self, key):
        if key in (0, len(self.seasons)):
            return self.seasons[key]
        return None
    
    
    class Season:
        def __init__(self, season) -> None:
            if not isinstance(season, list):
                self.__set_default__()
                return
            
            season = season[0]
            
            self.mode_slug: str     = th.parse_str(season.get("mode_slug"))
            self.season_slug: str   = th.parse_str(season.get("season_slug"))
            self.region_slug: str   = th.parse_str(season.get("region_slug"))
            self.rank_slug: str     = th.parse_str(season.get("rank_slug"))[3:]
            self.max_rank_slug: str = th.parse_str(season.get("max_rank_slug"))[3:]
            self.rank_image_url     = RoleDicts.ranks_pics.get(self.max_rank_slug)
            
            self.kills: int  = th.parse_int(season.get("kills"))
            self.deaths: int = th.parse_int(season.get("deaths"))
            self.kd: float   = th.parse_float(season.get("kd"))
            
            self.wins: int     = th.parse_int(season.get("wins"))
            self.losses: int   = th.parse_int(season.get("losses"))
            self.wl: float     = th.parse_float(season.get("wl"))
            self.abandons: int = th.parse_int(season.get("abandons"))
            
            self.mmr: int        = th.parse_int(season.get("mmr"))
            self.max_mmr: int    = th.parse_int(season.get("max_mmr"))
            self.mmr_change: int = th.parse_int(season.get("mmr_change"))
            self.mmr_point: str  = "ᐃ" if self.mmr_change > 0 else "ᐁ" if self.mmr_change < 0 else "ᐅ"
            self.mmr_change = abs(self.mmr_change)
            
            self.champion_position: int = th.parse_int(season.get("champion_position"))
            if self.champion_position > 0:
                self.rank_image_url = rank_champion_api.format(self.champion_position)
            

        def __set_default__(self):
            self.mode_slug: str = "N/A"
            self.season_slug: str = "N/A"
            self.region_slug: str = "N/A"
            self.max_rank_slug: str = "N/A"
            self.rank_image_url = rickroll_gif
            
            self.kills: int = 0
            self.deaths: int = 0
            self.kd: float = 0.0
            
            self.wins: int = 0
            self.losses: int = 0
            self.wl: float = 0.0
            self.abandons: int = 0
            
            self.mmr: int = 0
            self.max_mmr: int = 0
            self.mmr_change: int = 0
            self.mmr_point: str = "ᐅ"
            
            self.champion_position: int = 0
        
        
        def __repr__(self) -> str:
            s = ""
            season = self.season_slug.replace("-", " ").capitalize()
            s += f"Season: {season}\n"
            s += f"Mode: {self.mode_slug}\n"
            s += f"Region: {self.region_slug}\n"
            s += f"Rank: {self.rank_slug}\n"
            s += f"Max Rank: {self.max_rank_slug}\n"
            s += f"Kills: {self.kills}\n"
            s += f"Deaths: {self.deaths}\n"
            s += f"KD: {self.kd}\n"
            s += f"Wins: {self.wins}\n"
            s += f"Losses: {self.losses}\n"
            s += f"WL: {self.wl}\n"
            s += f"Abandons: {self.abandons}\n"
            s += f"MMR: {self.mmr}\n"
            s += f"Max MMR: {self.max_mmr}\n"
            s += f"MMR Change: {self.mmr_point}{self.mmr_change}\n"
            s += f"Champion Position: {self.champion_position}\n"
            
            return s
    
        
    def get(self, key: str) -> Season:
        if key in self.keys:
            return self.seasons[self.keys.index(key)]
        return self.seasons[0]
    
           
class Profile:
    def __init__(self, _json) -> None:
        self.__set_default__()
        if not _json:
            return
        
        self.__unpack_json__(_json)


    def __unpack_json__(self, _json):
        self.display_name : str  = th.parse_str(_json.get("display_name"))
        self.profile_views : int = th.parse_int(_json.get("profile_views"))
        
        self.user_id : str       = th.parse_str(_json.get("user_id"))
        self.player_id : str     = th.parse_str(_json.get("profile_id"))
        
        self.level : int         = th.parse_int(_json.get("level"))
        
        self.kd : float          = th.parse_float(_json.get("kd"))
        
        self.is_cheater        = th.parse_bool(_json.get("is_cheater"))
        self.is_vereified      = th.parse_bool(_json.get("is_verified"))
        self.display_ban : str = th.parse_str(_json.get("display_ban"))
        
        self.json_url    = api_url.format(self.user_id)
        self.avatar_url  = avatar_url.format(self.user_id)
        self.profile_url = profile_url.format(self.display_name, self.user_id)
        
        self.platform_slug : str      = th.parse_str(_json.get("platform_slug"))
        self.updated_at : datetime    = datetime.fromisoformat(
            _json.get("updated_at")
            )
        self.can_update_at : datetime = datetime.fromisoformat(
            _json.get("can_update_at")
            )
    
    
    def __set_default__(self):
        self.display_name: str = "N/A"
        self.profile_views: int = 0
        
        self.user_id: str = "N/A"
        self.player_id: str = "N/A"
        
        
        self.level: int = 0
        self.kd: float = 0.0
        
        self.is_cheater: bool = False
        self.is_vereified: bool = False
        self.display_ban: str = "N/A"
            
        self.json_url = my_git
        self.avatar_url = rickroll_gif
        self.profile_url = my_git
            
        self.updated_at: datetime = datetime.fromisoformat("1970-01-01T00:00:00+00:00")
        self.can_update_at: datetime = datetime.fromisoformat("1970-01-01T00:00:00+00:00")
        self.platform_slug: str = "N/A"

    
    def __repr__(self) -> str:
        s = ""
        s += f"========{self.display_name}========\n"
        s += f"User ID: {self.user_id}\n"
        s += f"Player ID: {self.player_id}\n"
        s += f"Platform: {self.platform_slug}\n"
        s += f"Level: {self.level}\n"
        s += f"KD: {self.kd}\n"
        s += f"Is Cheater: {self.is_cheater}\n"
        s += f"Is Verified: {self.is_vereified}\n"
        s += f"Display Ban: {self.display_ban}\n"
        s += f"Profile Views: {self.profile_views}\n"
        s += f"Updated At: {self.updated_at}\n"
        s += f"Can Update At: {self.can_update_at}\n"
        
        return s
        

class SummaryGraphData:
    def __init__(self, _json) -> None:
        if not _json or isinstance(_json, list):
            self.__set_default__()
            return
        
        self.ranked = SummaryGraphData.GraphData.generate(_json.get('ranked'))
        self.casual = SummaryGraphData.GraphData.generate(_json.get('casual'))
        self.deathmatch = SummaryGraphData.GraphData.generate(_json.get('deathmatch'))
        self.event = SummaryGraphData.GraphData.generate(_json.get('event'))


    def __set_default__(self):
        self.ranked = SummaryGraphData.GraphData.generate(None)
        self.casual = SummaryGraphData.GraphData.generate(None)
        self.deathmatch = SummaryGraphData.GraphData.generate(None)
        self.event = SummaryGraphData.GraphData.generate(None)
    
    
    class GraphData:
        def __init__(self, _json) -> None:
            if not _json:
                self.__set_default__()
                return
            
            self.kills: int  = th.parse_int(_json.get("kills"))
            self.deaths: int = th.parse_int(_json.get("deaths"))
            
            self.wins: int     = th.parse_int(_json.get("wins"))
            self.losses: int   = th.parse_int(_json.get("losses"))
            self.abandons: int = th.parse_int(_json.get("abandons"))
            
            self.lowest_mmr: int  = th.parse_int(_json.get("lowest_mmr"))
            self.highest_mmr: int = th.parse_int(_json.get("highest_mmr"))
            
            self.mode_slug: str = th.parse_str(_json.get("mode_slug"))
            self._date = date.fromisoformat(_json.get("date"))


        def __set_default__(self):
            self.kills: int = 0
            self.deaths: int = 0
            
            self.wins: int = 0
            self.losses: int = 0
            self.abandons: int = 0
            
            self.lowest_mmr: int = 0
            self.highest_mmr: int = 0
            
            self.mode_slug: str = "N/A"
            self._date: date = date.fromisoformat("1970-01-01")
        
        
        @classmethod
        def generate(cls, _json):
            if not _json or len(_json) == 0:
                return [cls(None)]
            return [cls(json) for json in _json]
        

class Alias:
    def __init__(self, _json) -> None:
        if not _json:
            self.display_name: str = "N/A"
            self.created_at: datetime = datetime.fromisoformat("1970-01-01T00:00:00+00:00")
            
            return
            
        self.display_name: str = th.parse_str(_json.get("display_name"))
        self.created_at: datetime = datetime.fromisoformat(_json.get("created_at"))
    

class GeneralRecords:
    def __init__(self, _json) -> None:
        if not _json:
            self.ranked = GeneralRecords.Record(None)
            self.records = _json
            
            return
        
        self.ranked  = GeneralRecords.Record(_json.get('ranked'))
        self.records = _json
        

    class Record:
        def __init__(self, _json) -> None:
            if not _json:
                self.__set_default__()
                
                return
            
            self.mode_slug: str = _json.get("mode_slug")
            
            self.kills: int     = int(_json.get("kills"))
            self.deaths: int    = int(_json.get("deaths"))
            self.kd: float      = float(_json.get("kd"))
            
            self.wins: int      = int(_json.get("wins"))
            self.losses: int    = int(_json.get("losses"))
            self.wl: float      = float(_json.get("wl"))
            self.abandons: int  = int(_json.get("abandons"))
            self.matched_count: int = self.wins + self.losses + self.abandons
            
            self.max_mmr: int   = int(_json.get("max_mmr"))

        def __set_default__(self):
            self.mode_slug: str = "N/A"
            
            self.kills: int = 0
            self.deaths: int = 0
            self.kd: float = 0.0
            
            self.wins: int = 0
            self.losses: int = 0
            self.wl: float = 0.0
            self.abandons: int = 0
            
            self.max_mmr: int = 0
            
            
class CurrentSeasonRecords:
    def __init__(self, _json) -> None:
        if not _json or isinstance(_json, list):
            self.ranked = CurrentSeasonRecords.Record(None)
            self.casual = CurrentSeasonRecords.Record(None)
            self.deathmatch = CurrentSeasonRecords.Record(None)
            self.event = CurrentSeasonRecords.Record(None)
            
            return
        
        self.ranked = CurrentSeasonRecords.Record(_json.get('ranked'))
        self.casual = CurrentSeasonRecords.Record(_json.get('casual'))
        self.deathmatch = CurrentSeasonRecords.Record(_json.get('deathmatch'))
        self.event = CurrentSeasonRecords.Record(_json.get('event'))
    
    
    def __repr__(self) -> str:
        s = ""
        s += f"Ranked:\n{self.ranked}"
        # s += f"Casual:\n{self.casual}"
        # s += f"Deathmatch:\n{self.deathmatch}"
        # s += f"Event:\n{self.event}"
        return s
    
    
    class Record:
        def __init__(self, _json) -> None:
            if not _json:
                self.__set_default__()
                return
            
            self.mode_slug:str       = th.parse_str(_json.get("mode_slug"))
            self.season_slug:str     = th.parse_str(_json.get("season_slug"))
            self.region_slug:str     = th.parse_str(_json.get("region_slug"))
            self.rank_slug:str       = th.parse_str(_json.get("rank_slug"))[3:]
            self.max_rank_slug:str   = th.parse_str(_json.get("max_rank_slug"))[3:]
            self.rank_image_url      = RoleDicts.ranks_pics.get(self.rank_slug)
            
            self.kills:int           = th.parse_int(_json.get("kills"))
            self.deaths:int          = th.parse_int(_json.get("deaths"))
            self.kd:float            = th.parse_float(_json.get("kd"))
            
            self.wins:int            = th.parse_int(_json.get("wins"))
            self.losses:int          = th.parse_int(_json.get("losses"))
            self.wl:float            = th.parse_float(_json.get("wl"))
            self.abandons:int        = th.parse_int(_json.get("abandons"))
            
            self.mmr:int             = th.parse_int(_json.get("mmr"))
            self.max_mmr:int         = th.parse_int(_json.get("max_mmr"))
            self.mmr_change:int      = th.parse_int(_json.get("mmr_change"))
            self.mmr_point: str = "ᐃ" if self.mmr_change > 0 else "ᐁ" if self.mmr_change < 0 else "ᐅ"
            self.mmr_change = abs(self.mmr_change)
            
            self.champion_position:int = th.parse_int(_json.get("champion_position"))
            if self.champion_position > 0:
                self.rank_image_url = rank_champion_api.format(self.champion_position)

        def __set_default__(self):
            self.mode_slug: str = "N/A"
            self.season_slug: str = "N/A"
            self.region_slug: str = "N/A"
            self.rank_slug: str = "N/A"
            self.max_rank_slug: str = "N/A"
            self.rank_image_url = rickroll_gif
            
            self.kills: int = 0
            self.deaths: int = 0
            self.kd: float = 0.0
            
            self.wins: int = 0
            self.losses: int = 0
            self.wl: float = 0.0
            self.abandons: int = 0
            
            self.mmr: int = 0
            self.max_mmr: int = 0
            self.mmr_change: int = 0
            self.mmr_point: str = "ᐅ"
            
            self.champion_position: int = 0
        

        def __repr__(self) -> str:
            s = ""
            s += f"Mode: {self.mode_slug}\n"
            s += f"Season: {self.season_slug}\n"
            s += f"Region: {self.region_slug}\n"
            s += f"Rank: {self.rank_slug}\n"
            s += f"Max Rank: {self.max_rank_slug}\n"
            s += f"Kills: {self.kills}\n"
            s += f"Deaths: {self.deaths}\n"
            s += f"KD: {self.kd}\n"
            s += f"Wins: {self.wins}\n"
            s += f"Losses: {self.losses}\n"
            s += f"WL: {self.wl}\n"
            s += f"Abandons: {self.abandons}\n"
            s += f"MMR: {self.mmr}\n"
            s += f"Max MMR: {self.max_mmr}\n"
            s += f"MMR Change: {self.mmr_point}{self.mmr_change}\n"
            s += f"Champion Position: {self.champion_position}\n"
            
            return s


class PlayerData:
    def __init__(self, _json):
        self.profile: Profile = Profile(_json.get('profile'))
        self.name = self.profile.display_name
        self.leaderboard: int = _json.get('leaderboard')
        
        self.summary_graph_data: SummaryGraphData = SummaryGraphData(_json.get('summary_graph_data'))
        
        self.social_profile = _json.get('social_profile')
        self.game_bans = _json.get('game_bans')
        self.profile_bans = _json.get('profile_bans')
        self.external_bans = _json.get('external_bans')
        
        if _json.get("aliases") is not None:
            self.aliases: list[Alias] = [Alias(x) for x in _json.get("aliases")]
        else:    
            self.aliases = _json.get('aliases')
        
        self.general_records: GeneralRecords = GeneralRecords(_json.get('general_records'))
        self.current_season_records: CurrentSeasonRecords = CurrentSeasonRecords(_json.get('current_season_records'))
        self.past_season_ranked_records: PastSeasonRankedRecords = PastSeasonRankedRecords(_json.get('past_season_ranked_records'))
        self.top_region: str = _json.get('top_region')
        self.region_breakdown = _json.get('region_breakdown')
        if _json.get("last_played_at") is not None:
            self.last_played_at: datetime = datetime.fromisoformat(_json.get('last_played_at'))
        else:
            self.last_played_at = datetime.fromisoformat("1970-01-01T00:00:00+00:00")

        if self.current_season_records.ranked is not None:
            self.is_full = True
        
    
    @property
    def seasons(self) -> list[str]:
        return self.past_season_ranked_records.keys
    
    
    def get_current_season_record(self) -> str:
        return f"Player: {self.name}\n{self.current_season_records}"
    
    
    def get_season_record(self, season: str) -> PastSeasonRankedRecords.Season:
        return self.past_season_ranked_records.get(season)
    
    
    def __repr__(self) -> str:
        return f"Player: {self.name}\n{self.profile}"
