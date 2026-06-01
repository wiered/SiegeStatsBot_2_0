import discord

from discord import Interaction, ui
from discord import ButtonStyle, SelectOption

from core import user
from core.player_data import PlayerData
from core.player_data_models import NormalizedProfile
from db.db import users_db

default_footer = "R6HubBot • https://github.com/wiered"


def format_ui_number(value: int | float) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


# ========================= #
# Buttons                   #


class AccountConfirmButton(ui.Button):
    def __init__(
        self,
        d_id: int,
        username: str,
        confirmed: bool,
        *args,
        **kwargs,
    ):
        super().__init__(
            label="Yes" if confirmed else "No",
            custom_id=f"account-confirm:{d_id}:{'yes' if confirmed else 'no'}",
            style=ButtonStyle.green if confirmed else ButtonStyle.red,
            *args,
            **kwargs,
        )
        self.__d_id = d_id
        self.__username = username
        self.__confirmed = confirmed

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.__d_id:
            await interaction.response.send_message(
                "This confirmation is not for you.",
                ephemeral=True,
            )
            return

        if not self.__confirmed:
            await interaction.response.edit_message(
                content="Authorization canceled.",
                embed=None,
                view=None,
            )
            return

        await interaction.response.defer()
        _user = await user.User.create(d_id=self.__d_id, siege_id=self.__username)
        users_db.add_user(_user)

        if interaction.message:
            _view = SeasonsView(_user.player_data, self.__d_id)
            await interaction.message.edit(
                content=f"Authorized as {_user.name}",
                embed=ProfileEmbed(_user.player_data, self.__d_id),
                view=_view,
            )


class GitHubButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="GitHub",
            style=ButtonStyle.link,
            url="https://github.com/wiered",
        )


class R6DataButton(ui.Button):
    def __init__(self, url: str):
        super().__init__(
            label="R6Data",
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
        await interaction.response.defer()
        _user = await user.User.create(d_id=self.__d_id, siege_id=str(self.__user_id))

        embed = ProfileEmbed(_user.player_data, self.__d_id, season=self.values[0])
        _view = SeasonsView(_user.player_data, self.__d_id)

        if embed and interaction.message:
            await interaction.message.edit(embed=embed, view=_view)


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
                    emoji="<:deadbydaylight:848916323962060860>",
                    value="Dead by Daylight",
                ),
            ],
            row=0,
        )


# ========================= #
# Views                     #


class SeasonsView(ui.View):
    def __init__(self, player, d_id: int, timeout: float = 180):
        self.player = player
        self.d_id = d_id
        super().__init__(timeout=timeout)
        self.generate_seasons_select()

    def gen_season_option(self, season_slug):
        label = self.player.season_labels.get(season_slug, season_slug)
        _option = SelectOption(
            label=label.replace("-", " ").capitalize(),
            value=str(season_slug),
            emoji="🥕",
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
            options=options,
        )

        return _select

    def generate_options(self):
        options = []
        for _season in self.player.seasons:
            options.append(self.gen_season_option(_season))

        return options

    def generate_seasons_select(self, season: str = "Current Season"):
        options = self.generate_options()

        options.insert(0, self.gen_season_option("Current Season"))

        self.add_item(
            self.get_std_select(
                options=options,
                placeholder=season.replace("-", " ").capitalize(),
            )
        )

        url = self.player.profile.profile_url

        self.add_item(R6DataButton(url))
        self.add_item(GitHubButton())


class AccountConfirmView(ui.View):
    def __init__(self, profile: NormalizedProfile, d_id: int):
        super().__init__(timeout=180)
        self.profile = profile
        self.d_id = d_id
        self.generate_buttons()

    def generate_buttons(self):
        self.add_item(
            AccountConfirmButton(
                d_id=self.d_id,
                username=self.profile.display_name,
                confirmed=True,
            )
        )
        self.add_item(
            AccountConfirmButton(
                d_id=self.d_id,
                username=self.profile.display_name,
                confirmed=False,
            )
        )


# ========================= #
# Embeds                    #


class ProfileEmbed(discord.Embed):
    def __init__(self, player: PlayerData, d_id: int, season: str = ""):
        self.player = player
        self.d_id = d_id
        self.season = season
        super().__init__(
            title="R6Data", url=self.player.profile.profile_url, color=0x039BBA
        )
        self.generate_player_embed(season)

    def _set_defaults(self):
        """Set default emded params"""
        self.set_author(
            name=self.player.name,
            url=self.player.profile.profile_url,
            icon_url=self.player.profile.avatar_url,
        )
        self.add_field(
            name="General:",
            value="Level **{}**\nPlatform: **{}**".format(
                format_ui_number(self.player.profile.level),
                self.player.profile.platform_slug.replace("-", " ").capitalize(),
            ),
            inline=True,
        )

        self.set_thumbnail(url=self.player.current_season_records.ranked.rank_image_url)
        self.set_footer(text=default_footer)

    def _add_std_fields(self, record):
        self.add_field(
            name="RP:",
            value="**{}**\n{}\nMAX **{}**".format(
                format_ui_number(record.mmr),
                f"{record.mmr_point}{format_ui_number(record.mmr_change)}",
                format_ui_number(record.max_mmr),
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
            value="**{}**\nKills **{}**\nDeaths **{}**".format(
                format_ui_number(record.kd),
                format_ui_number(record.kills),
                format_ui_number(record.deaths),
            ),
            inline=True,
        )
        self.add_field(
            name="SeasonalWL:",
            value="**{}**\nWins **{}**\nLosses **{}**".format(
                f"{format_ui_number(record.wl * 100)}%",
                format_ui_number(record.wins),
                format_ui_number(record.losses),
            ),
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


class AccountConfirmEmbed(discord.Embed):
    def __init__(self, profile: NormalizedProfile, search_request: str):
        self.profile = profile
        self.search_request = search_request
        super().__init__(
            title="Is this your account?",
            url=profile.profile_url,
            color=0x039BBA,
        )
        self.gen_stds()

    def gen_stds(self):
        self.set_author(
            name=self.profile.display_name or self.search_request,
            url=self.profile.profile_url,
            icon_url=self.profile.avatar_url,
        )
        self.add_field(
            name="Username:",
            value=f"**{self.profile.display_name or self.search_request}**",
            inline=True,
        )
        self.add_field(
            name="Platform:",
            value=f"**{self.profile.platform_slug.replace('-', ' ').capitalize()}**",
            inline=True,
        )
        self.add_field(
            name="Level:",
            value=f"**{format_ui_number(self.profile.level)}**",
            inline=True,
        )
        if self.profile.avatar_url:
            self.set_thumbnail(url=self.profile.avatar_url)
        self.set_footer(text=default_footer)


class AuthorizedEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="You alredy authorized!", color=0x039BBA)
        self.set_footer(text=default_footer)


class UnauthorizedEmbed(discord.Embed):
    def __init__(self) -> None:
        super().__init__(title="No such user in base!", color=0x039BBA)
        self.set_footer(text=default_footer)


class NoSearchResultEmbed(discord.Embed):
    def __init__(self, search_request: str) -> None:
        super().__init__(
            title=f'No results found for "{search_request}"!', color=0x039BBA
        )
        self.set_footer(text=default_footer)
