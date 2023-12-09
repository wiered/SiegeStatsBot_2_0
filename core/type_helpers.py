""" Get variable from json. Used for strong typing

    Args:
        _json (dict): json with player data

    Returns:
        typed variable
"""  

def get_siege_id(_json) -> str:
    if isinstance(_json.get("id"), str):
        return _json["id"]
    return ""

def get_d_id(_json) -> int:
    if _json.get("d_id"):
        return int(_json["d_id"])
    return 0

def get_rank_from_json(_json) -> str:
    if _json.get("rank"):
        return _json["rank"]
    return "Unranked"

def get_name_from_json(_json) -> str:
    if _json.get("name"):
        return _json["name"]
    return ""


def parse_str(key) -> str:
    if not key:
        return "N/A"
    
    if isinstance(key, str):
        return key
    
    return "N/A"


def parse_int(key) -> int:
    if not key:
        return 0
    
    if isinstance(key, int):
        return key
    
    if key[0] == "-":
        key = key[1:]
        
    if key.isnumeric():
        return int(key)
    
    return 0


def parse_float(key) -> float:
    if not key:
        return 0.0
    
    if isinstance(key, float) or isinstance(key, int):
        return key  
    
    _key = key.replace(".", "", 1)
    if key[0] == "-":
        _key = _key[1:]
        
    if _key.isnumeric():
        return float(key)
    
    return 0.0


def parse_bool(key) -> bool:
    if not key:
        return False
    
    if isinstance(key, bool):
        return key
    
    if key == "true":
        return True
    
    return False
