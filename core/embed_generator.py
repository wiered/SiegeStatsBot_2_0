import string

import discord
from discord import ButtonStyle, SelectOption
from discord import Embed
from discord import ui
from discord.ui import Select

from bot import (
    AuthButton, 
    SeasonSelect,
    SearchButton
)

default_footer = "R6HubBot • https://github.com/wiered"

class StdEmbeds:
    def authorized_embed(self) -> Embed:
        return Embed(title="You alredy authorized!",color=0x039BBA).set_footer(text=default_footer)
    
    def not_authorized_embed(self) -> Embed:
        return Embed(title="No such user in base!",color=0x039BBA).set_footer(text=default_footer)
    
    def no_search_result(self, search_request: str) -> Embed:
        return Embed(title=f"No results found for \"{search_request}\"!",color=0x039BBA).set_footer(text=default_footer)
    
    def no_seasons_select(self) -> Select:
        return Select(
            custom_id="seasons_select",
            placeholder="No seasons found", 
            disabled=True,
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Dead by Daylight", emoji='<:deadbydaylight:848916323962060860>', value='Dead by Daylight'),
                ],
            row=0
            )
    
    

def generate_player_embed(_json: dict) -> Embed:
    """Generate discord embed from user's stats

    Args:
        _json (dict): raw user stats

    Returns:
        Embed: discord embed
    """
    
    embed, rank = __get_defaults__(_json)
    if _json.get("rank"):
        embed.add_field(
            name="Rank",
            value=rank,
            inline=False,
        )
    if _json.get("is_full"):
        embed.add_field(
            name="Stats:",
            value = """MMR: {} {}
            KD: {}
            {} wl in {} Matches
            """.format(
                _json.get("mmr"), 
                _json.get("mmr_change"), 
                _json.get("kd"), 
                _json.get("wl"), 
                _json.get("matches")
            ),
            inline=False,
        )
    return embed


def generate_past_season(_json: dict) -> Embed:
    """Generate discord embed from user's past season stats

    Args:
        _json (dict): raw user stats

    Returns:
        Embed: discord embed
    """    
    
    embed, rank = __get_defaults__(_json)
    
    season = __get_capitalized__(_json.get("season"))
    embed.add_field(name="Season", value=season, inline=False)
    if _json.get("rank"):
        embed.add_field(name="Max Rank", value=rank, inline=False)

    if _json.get("is_full"):
        std_value = "MAX MMR: {} \nKD: {} \n{} wl in {} Matches"
        embed.add_field(
            name="Stats:",
            value = std_value.format(
                _json.get("mmr"),  
                _json.get("kd"), 
                _json.get("wl"), 
                _json.get("matches")
            ),
            inline=False
        )
    
    return embed

def __get_defaults__(_json):
    embed = Embed(title="Tabstats", url=_json.get("profile_url"), color=0x039BBA)
    embed.set_author(
            name=_json.get("name"), 
            url=_json.get("profile_url"), 
            icon_url=_json.get("avatar_url")
        )
    embed.set_thumbnail(url=_json.get("rank_image_url"))
    embed.set_footer(text=default_footer)
    
    rank = __get_capitalized__(_json.get("rank"))
    return embed,rank


def __get_capitalized__(string) -> str:
    if string is not None and isinstance(string, str):
        string = string.capitalize()
    if string is not None:
        return string
    return "Season Name"

    
def generate_search_embed(users_list, search_request) -> Embed:
    # search_results: [json_unpacker.unpack_json(_json) for _json in response.json()]
    if not search_request:
        return StdEmbeds().no_search_result("None")
    
    embed = Embed(color=0x039BBA)
    embed.set_author(
        name="Search for {}:".format(search_request)
    )
    embed.set_footer(text=default_footer)
    
    if not users_list:
        return StdEmbeds().no_search_result(search_request)
        
    
    i = 1
    embed_value = "Level: {:3} {:6} Rank: {:10}"
    nbsp = "᲼"
    for user in users_list:
        level = str(user["level"]) + (3 - len(str(user["level"])))*nbsp
        embed.add_field(
            name=f"{i}. {user['name']}",
            value=embed_value.format(level, 4*nbsp, user["rank"]),
            inline=False,
        )
        i+=1
    
    return embed
        

def generate_buttons(_users_list: list, d_id: int, auth = False) -> ui.View:
        _view = ui.View()
        gen_btn = __generate_auth_button__ if auth else __generate_search_button__
        for i in range(len(_users_list)):
            _view.add_item(gen_btn(d_id, i, _users_list[i]))
            
        return _view

def __generate_auth_button__(d_id, i, _):
    _button = AuthButton(
        d_id=d_id,
        label=str(i+1), 
        custom_id=_.get("id"), 
        style=ButtonStyle.green,
        row=i//4
    )
    
    return _button


def __generate_search_button__(d_id, i, _):
    _button = SearchButton(
        d_id=d_id,
        label=str(i+1), 
        custom_id=_.get("id"), 
        style=ButtonStyle.green,
        row=i//4
    )
    
    return _button
    

def seasons_select(_json: dict, d_id: int, name, user_id) -> ui.View:
    _seasons = _json.get("past_season_ranked_records")
    if not _seasons:
        return ui.View().add_item(StdEmbeds().no_seasons_select())
    
    options = [__gen_season_option__(i, _seasons[i][0].get("season_slug")) for i in range (len(_seasons)) if _seasons[i][0].get("season_slug") is not None]
    
    return ui.View().add_item(__get_std_select__(d_id, name, user_id, options))


def __gen_season_option__(i, season_slug):
    _option = SelectOption(
        label=season_slug.replace("-", " ").capitalize(), 
        value=str(i),
        emoji="🥕"
    )
    
    return _option


def __get_std_select__(d_id: int, name, user_id, options: list) -> SeasonSelect:
    _select = SeasonSelect(
        d_id=d_id,
        name=name,
        user_id=user_id,
        custom_id="seasons_select",
        placeholder="Select a season",
        disabled=False,
        min_values=1,
        max_values=1,
        row=0,
        options=options
    )
    
    return _select