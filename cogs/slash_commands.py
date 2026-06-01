from discord import app_commands
from discord.ext import commands
from discord import ui as ui_discord
from discord import Interaction

from cogs import ui as ui_cogs
from core import parser
from core import user
from db.db import users_db


class HubTree(commands.Cog):
    hub_group = app_commands.Group(name="hub", description="Hub commands")
    sielent = app_commands.Group(name="sielent", description="Sielent mode")

    def __init__(self, bot):
        self.bot = bot

    @hub_group.command(name="stats", description="Get siege stats")
    async def stats(self, ctx, name: str = ""):
        if not name:
            return await self.__get_self_stats__(ctx)
        return await self.__get_player_stats__(ctx, name, ephemeral=False)

    @sielent.command(name="stats", description="Get siege stats. Will see only you")
    async def sielent_stats(self, ctx, name: str = ""):
        if not name:
            return await self.__get_self_stats__(ctx, ephemeral=True)
        return await self.__get_player_stats__(ctx, name, ephemeral=True)

    @hub_group.command(name="authorize", description="Authorize your account")
    async def auth(self, interaction: Interaction, name: str) -> None:
        if not name or len(name) < 3:
            return await interaction.response.send_message("Please provide your name!")

        if interaction.user.id in users_db.keys:
            return await interaction.response.send_message(
                embed=ui_cogs.AuthorizedEmbed(), ephemeral=True
            )

        await self.__get_account_confirmation__(interaction, name)

    async def __get_account_confirmation__(
        self,
        interaction: Interaction,
        name: str,
    ):
        await interaction.response.defer(ephemeral=True)

        async with parser.Parser() as p:
            profile = await p.get_account_profile(name)

        if profile is None:
            return await interaction.followup.send(
                embed=ui_cogs.NoSearchResultEmbed(name),
                ephemeral=True,
            )

        embed = ui_cogs.AccountConfirmEmbed(profile, name)
        view = ui_cogs.AccountConfirmView(profile, interaction.user.id)
        return await interaction.followup.send(
            embed=embed,
            view=view,
            ephemeral=True,
        )

    async def __get_player_stats__(
        self,
        interaction: Interaction,
        name: str,
        ephemeral: bool = False,
    ):
        await interaction.response.defer(ephemeral=ephemeral)

        async with parser.Parser() as p:
            profile = await p.get_account_profile(name)

        if profile is None:
            return await interaction.followup.send(
                embed=ui_cogs.NoSearchResultEmbed(name),
                ephemeral=ephemeral,
            )

        _user = await user.User.create(
            d_id=interaction.user.id,
            siege_id=profile.display_name,
        )
        embed = ui_cogs.ProfileEmbed(_user.player_data, interaction.user.id)
        _view = ui_cogs.SeasonsView(_user.player_data, interaction.user.id)

        return await interaction.followup.send(
            embed=embed,
            view=_view,
            ephemeral=ephemeral,
        )

    async def __get_self_stats__(
        self, interaction: Interaction, ephemeral: bool = False
    ):
        _user = users_db.get_user(interaction.user.id)
        if not _user:
            return await interaction.response.send_message(
                embed=ui_cogs.UnauthorizedEmbed(), ephemeral=ephemeral
            )

        await interaction.response.defer(ephemeral=ephemeral)
        await _user.parse_data()
        embed = ui_cogs.ProfileEmbed(_user.player_data, interaction.user.id)

        _view = ui_discord.View()
        _view.add_item(ui_cogs.NoSeasonsSelect())
        _view = ui_cogs.SeasonsView(_user.player_data, interaction.user.id)

        return await interaction.followup.send(
            embed=embed, view=_view, ephemeral=ephemeral
        )


async def setup(bot):
    await bot.add_cog(HubTree(bot))
