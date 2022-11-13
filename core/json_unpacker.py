from core.data import APIUrls, RoleDicts
from core.user import User

def unpack_json(response, full=False) -> dict:
    """Unpack json from api to dict

    Args:
        response (_type_): raw json from api
        full (bool, optional): if true, unpacking from full json. Defaults to False.

    Returns:
        dict: unpacked json with player data
    """
    
    if not response:
        return {}
    _json = __unpack_defaults__(response)
    
    
    if full:
        return __unpack_full_json__(response,  _json)
    
    return __unpack_partial_json(response,  _json)


def __unpack_defaults__(response) -> dict:
    """_summary_: Unpack default data from json from api

    Args:
        response (_type_): raw json from api

    Returns:
        dict: unpacked json with std player data
    """
    
    _json = {}
    _json.update({"is_full": False})
    
    _json.update({"name": response["profile"]["display_name"]})
    _json.update({"id": response["profile"]["user_id"]})
    _json.update({"level": response["profile"]["level"]})
    if not _json.get("level"):
        _json.update({"level": 0})
    
    _json.update({"rank": "N/A"})

    profile_url = APIUrls.tabstats_profie_url.format(   
        response["profile"]["display_name"], 
        response["profile"]["user_id"]
        )
    _json.update({"profile_url" : profile_url})
    _json.update({"avatar_url": f'https://ubisoft-avatars.akamaized.net/{response["profile"]["user_id"]}/default_146_146.png'})
    
    return _json


def __unpack_partial_json(response, _json) -> dict:
    """Unpack json from api/search results

    Args:
        response (_type_): raw json from api
        _json (_type_): unpacked json with std player data

    Returns:
        dict: unpacked json with player data
    """
    
    csrr = "current_season_ranked_record"
    
    if not response[csrr]:
        return _json
    
    _json.update({"is_full": True})
    _json.update({"rank": response[csrr]["rank_slug"][3:]})
    _json.update({"mmr" : response[csrr]["mmr"]})
    _json.update({"mmr_change" : response[csrr]["mmr_change"]})
    _json.update({"kd" : response[csrr]["kd"]})
    _json.update({"wl" : response[csrr]["wl"]})
    
    rank = RoleDicts.Ranks_with_nums.get(response[csrr]["rank_slug"][3:])
    if rank is not None:
        rank_img_url = RoleDicts.ranks_pics.get(rank)
        if rank_img_url is not None:
            _json.update({"rank_image_url": rank_img_url})
    
    matches = int(response[csrr]["wins"]) + int(response[csrr]["losses"])
    _json.update({"matches" : matches})
    
    _json = __get_mmr_change__(_json)
                 
    return _json


def __unpack_full_json__(response, _json) -> dict:
    """Unpack full json from api/players

    Args:
        response (_type_): raw json from api
        _json (_type_): unpacked json with std player data

    Returns:
        dict: unpacked json with player data
    """
    
    
    csrr = "current_season_records"
        
    if not response[csrr]:
        return _json
    
    if not response[csrr]["ranked"]:
        return _json
    
    _json.update({"is_full": True})
    _json.update({"rank": response[csrr]["ranked"]["rank_slug"][3:]})
    _json.update({"mmr" : response[csrr]["ranked"]["mmr"]})
    _json.update({"mmr_change" : response[csrr]["ranked"]["mmr_change"]})
    _json.update({"kd" : response[csrr]["ranked"]["kd"]})
    _json.update({"wl" : response[csrr]["ranked"]["wl"]})
    
    rank = RoleDicts.Ranks_with_nums.get(response[csrr]["ranked"]["rank_slug"][3:])
    if rank is not None:
        rank_img_url = RoleDicts.ranks_pics.get(rank)
        if rank_img_url is not None:
            _json.update({"rank_image_url": rank_img_url})
    
    wins = response[csrr]["ranked"]["wins"]
    loses = response[csrr]["ranked"]["losses"]
    _json.update({"matches" : int(wins) + int(loses)})
    
    _json = __get_mmr_change__(_json)
                
    return _json


def __get_mmr_change__(_json: dict) -> dict:
    mmr_change = _json.get("mmr_change")
    if not (mmr_change is not None or isinstance(mmr_change, int)):
        return _json
    
    if mmr_change >= 0:
        _json.update({"mmr_change": f'ᐃ{mmr_change}'})
    else:
        _json.update({"mmr_change": f'ᐁ{abs(mmr_change)}'})
        
    return _json


def unpack_season_json(response:dict, season: int) -> dict:
    _json = __unpack_defaults__(response)
    seasons = response.get("past_season_ranked_records")
    
    if not seasons:
        return _json
        
    if not (0 <= season < len(seasons)):
        return _json
    
    seasons = seasons[season][0]
    
    _json.update({"is_full": True})
    _json.update({"season": seasons.get("season_slug").replace("-", " ")})
    _json.update({"rank": seasons["max_rank_slug"][3:]})
    _json.update({"mmr" : seasons["max_mmr"]})
    _json.update({"mmr_change" : seasons["mmr_change"]})
    _json.update({"kd" : seasons["kd"]})
    _json.update({"wl" : seasons["wl"]})
    
    rank = RoleDicts.Ranks_with_nums.get(seasons["max_rank_slug"][3:])
    if rank is not None:
        rank_img_url = RoleDicts.ranks_pics.get(rank)
        if rank_img_url is not None:
            _json.update({"rank_image_url": rank_img_url})
    
    wins = seasons["wins"]
    losses = seasons["losses"]    
    _json.update({"matches" : int(wins) + int(losses)})
    
    
    return _json

def generate_user_data(user: User) -> dict:
    """Generate user data from json

    Args:
        user (core.user.User): user object

    Returns:
        dict: std user data
    """    
    
    
    return {
        "name": user.name,
        "siege_id": user.siege_id,
        "d_id": user.d_id,
        "rank": user.rank,
    }
    
    