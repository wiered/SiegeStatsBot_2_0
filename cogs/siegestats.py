from discord import ui
from discord.ext import commands

from cogs import ui as ui_cogs
from core import parser
from core import user
from db.db import users_db


class SiegeStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, name: str = ""):
        if not name:
            return await self.__get_self_stats__(ctx)
        return await self.__get_player_stats__(ctx, name)

    async def __get_player_stats__(self, ctx, name: str):
        with parser.Parser() as p:
            profile = p.get_account_profile(name)

        if profile is None:
            await ctx.send(embed=ui_cogs.NoSearchResultEmbed(name), delete_after=1800)
            return await ctx.message.delete()

        _user = user.User(d_id=ctx.author.id, siege_id=profile.display_name)
        embed = ui_cogs.ProfileEmbed(_user.player_data, ctx.author.id)
        _view = ui_cogs.SeasonsView(_user.player_data, ctx.author.id)
        await ctx.send(embed=embed, view=_view, delete_after=1800)
        return await ctx.message.delete()

    async def __get_self_stats__(self, ctx):
        _user = users_db.get_user(ctx.author.id)
        if not _user:
            return await ctx.send(embed=ui_cogs.UnauthorizedEmbed())

        embed = ui_cogs.ProfileEmbed(_user.player_data, ctx.author.id)

        _view = ui.View()
        _view.add_item(ui_cogs.NoSeasonsSelect())
        _view = ui_cogs.SeasonsView(_user.player_data, ctx.author.id)

        return await ctx.send(embed=embed, view=_view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx):
        await ctx.channel.clone(name=ctx.channel.name, reason="Clearing channel")
        await ctx.channel.delete(reason="Clearing channel")


async def setup(bot):
    await bot.add_cog(SiegeStats(bot))
