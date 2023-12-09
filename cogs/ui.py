import discord

from discord import Interaction, ui
from discord import ButtonStyle, SelectOption
from discord import Embed
from discord import ui
from discord.ui import Select

from core import user
from core.player_data import PlayerData
from db.db import users_db

default_footer = "R6HubBot • https://github.com/wiered"

# ========================= #
# Buttons                   #


class AuthButton(ui.Button):
    def __init__(self, d_id: int, i, _, *args, **kwargs):
        super().__init__(
            label=str(i+1),
            custom_id=_.get("id"),
            style=ButtonStyle.green,
            row=i//4,
            *args,
            **kwargs
            )
        self.__d_id = d_id

    async def callback(self, interaction: Interaction):
        _user = user.User(d_id=self.__d_id, siege_id=str(self.custom_id))
        users_db.add_user(_user)

        if interaction.message:
            _view = SeasonsView(_user.player_data, self.__d_id)
            await interaction.response.edit_message(
                content=f"Authorized as {_user.name}",
                embed=ProfileEmbed(_user.player_data, self.__d_id),
                view=_view
            )


class SearchButton(ui.Button):
    def __init__(self, d_id: int, i, _, *args, **kwargs):
        super().__init__(
            label=str(i+1),
            custom_id=_.get("id"),
            style=ButtonStyle.green,
            row=i//4,
            *args,
            **kwargs
            )
        self.__d_id = d_id

    async def callback(self, interaction: Interaction):
        _user = user.User(d_id = self.__d_id, siege_id=str(self.custom_id))
        if interaction.message:
            _view = SeasonsView(_user.player_data, self.__d_id)
            await interaction.response.edit_message(
                content=f"Stats for {_user.name}",
                embed=ProfileEmbed(_user.player_data, self.__d_id),
                view=_view
            )


class GitHubButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="GitHub",
            style=ButtonStyle.link,
            url="https://github.com/wiered",
        )


class TabstatsButton(ui.Button):
    def __init__(self, url: str):
        super().__init__(
            label="Tabstats",
            style=ButtonStyle.link,
            url=url,
        )


# ========================= #
# Selects                   #

class SeasonSelect(ui.Select):
    def __init__(self, d_id: int, name, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__d_id = d_id
        self.__user_name = str(name)
        self.__user_id = user_id

    async def callback(self, interaction: Interaction):
        _user = user.User(d_id=self.__d_id, siege_id=str(self.__user_id))

        embed = ProfileEmbed(_user.player_data, self.__d_id, season=self.values[0])
        _view = SeasonsView(_user.player_data, self.__d_id)

        if embed:
            await interaction.response.edit_message(
                embed=embed,
                view=_view
            )


class NoSeasonsSelect(ui.Select):
    def __init__(self) -> None:
        super().__init__(
            custom_id="seasons_select",
            placeholder="No seasons found",
            disabled=True,
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="Dead by Daylight",
                    emoji='<:deadbydaylight:848916323962060860>',
                    value='Dead by Daylight'
                    ),
                ],
            row=0
        )


# ========================= #
# Views                     #

class SeasonsView(ui.View):
    def __init__(self, player, d_id: int, timeout: float = 180):
        self.player = player
        self.d_id = d_id
        super().__init__(timeout=timeout)
        self.generate_seasons_select()

    @staticmethod
    def gen_season_option(season_slug):
        _option = SelectOption(
            label=season_slug.replace("-", " ").capitalize(),
            value=str(season_slug),
            emoji="🥕"
        )

        return _option

    def get_std_select(self, options: list[SelectOption], placeholder) -> SeasonSelect:
        _select = SeasonSelect(
            d_id=self.d_id,
            name=self.player.profile.display_name.replace("-", " ").capitalize(),
            user_id=self.player.profile.user_id,
            custom_id="seasons_select",
            placeholder=placeholder,
            disabled=False,
            min_values=1,
            max_values=1,
            row=0,
            options=options
        )

        return _select

    def generate_options(self):
        options = []
        for _season in self.player.seasons:
            options.append(
                self.gen_season_option(
                    _season
                )
            )

        return options

    def generate_seasons_select(self, season: str = "Current Season"):
        options = self.generate_options()

        options.insert(
            0,
            self.gen_season_option(
                "Current Season"
            )
        )

        self.add_item(
            self.get_std_select(
                options=options,
                placeholder=season.replace("-", " ").capitalize(),
            )
        )

        url = self.player.profile.profile_url

        self.add_item(TabstatsButton(url))
        self.add_item(GitHubButton())


class SearchButtonsView(ui.View):
    def __init__(self, search_results: list, d_id: int, auth = False):
        super().__init__(timeout=180)
        self.search_results = search_results
        self.d_id = d_id
        self.auth = auth
        self.generate_buttons()

    def generate_buttons(self):
        for i in range(len(self.search_results)):
            _button = AuthButton(self.d_id, i, self.search_results[i]) if self.auth else SearchButton(self.d_id, i, self.search_results[i])
            self.add_item(_button)


# ========================= #
# Embeds                    #

class ProfileEmbed(discord.Embed):
    def __init__(self, player: PlayerData, d_id: int, season: str = ""):
        self.player = player
        self.d_id = d_id
        self.season = season
        super().__init__(
            title="Tabstats",
            url=self.player.profile.profile_url,
            color=0x039BBA
        )
        self.generate_player_embed(season)

    def _set_defaults(self):
        """ Set default emded params
        """
        self.set_author(
            name=self.player.name,
            url=self.player.profile.profile_url,
            icon_url=self.player.profile.avatar_url,
        )
        self.add_field(
            name="General:",
            value="Level **{}**\nPlatform: **{}**".format(
                self.player.profile.level,
                self.player.profile.platform_slug.replace("-", " ").capitalize()
                ),
            inline=True,
        )

        self.set_thumbnail(
            url=self.player.current_season_records.ranked.rank_image_url
        )
        self.set_footer(text=default_footer)

    def _add_std_fields(self, record):
        self.add_field(
            name="MMR:",
            value="**{}**\n{}\nMAX **{}**".format(
                record.mmr,
                f"{record.mmr_point}{record.mmr_change}",
                record.max_mmr,
                ),
            inline=True,
        )
        self.add_field(
            name="Rank:",
            value="**{}**\nMax **{}**".format(
                record.rank_slug.replace("-", " ").capitalize(),
                record.max_rank_slug.replace("-", " ").capitalize(),
                ),
            inline=True,
        )
        self.add_field(
            name="SeasonalKD:",
            value = "**{}**\nKills **{}**\nDeaths **{}**".format(
                record.kd,
                record.kills,
                record.deaths,
                ),
            inline=True,
        )
        self.add_field(
            name="SeasonalWL:",
            value="**{}**\nWins **{}**\nLosses **{}**".format(
                f"{record.wl*100}%",
                record.wins,
                record.losses,
                ),
            inline=True,
        )
        self.add_field(
            name="Bans(WIP):",
            value="None",
            inline=True,
        )

        if self.season != "":
            self.set_thumbnail(url=record.rank_image_url)
            season = record.season_slug.replace("-", " ").capitalize()
            self.set_footer(text=f"{season} • {default_footer}")

    def generate_player_embed(self, season: str = ""):
        """Generate discord embed from user's stats

        Args:
            season (dict): season name

        Returns:
            Embed: discord embed
        """

        record = self.player.current_season_records.ranked
        if season:
            record = self.player.get_season_record(season)

        self._set_defaults()
        self._add_std_fields(record)


class SearchEmbed(discord.Embed):
    def __init__(self, users_list, search_request):
        self.users_list = users_list
        self.search_request = search_request
        super().__init__(color=0x039BBA)

        if search_request and users_list:
            self.gen_stds()

        if not search_request:
            self = NoSearchResultEmbed(search_request="N/A")

        if not users_list:
            self = NoSearchResultEmbed(search_request=search_request)

    def gen_stds(self):
        self.set_author(name="Search for {}:".format(self.search_request))
        self.set_footer(text=default_footer)

        embed_value = "Level: {:3} {:6} Rank: {:10}"
        nbsp = "᲼"
        for i, _user in enumerate(self.users_list):
            level = (
                str(_user["level"]) +
                (
                    3 - len(str(_user["level"]))
                ) * nbsp
            )
            self.add_field(
                name=f"{i+1}. {_user['name']}",
                value=embed_value.format(level, 4 * nbsp, _user["rank"]),
                inline=False,
            )


class AuthorizedEmbed(discord.Embed):
    def __init__(self):
        super().__init__(
            title="You alredy authorized!",
            color=0x039BBA
        )
        self.set_footer(text=default_footer)


class UnauthorizedEmbed(discord.Embed):
    def __init__(self) -> None:
        super().__init__(
            title="No such user in base!",
            color=0x039BBA
        )
        self.set_footer(text=default_footer)


class NoSearchResultEmbed(discord.Embed):
    def __init__(self, search_request: str) -> None:
        super().__init__(
            title=f"No results found for \"{search_request}\"!",
            color=0x039BBA
        )
        self.set_footer(text=default_footer)
