"""_summary_: Get variable from json. Used for strong typing

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