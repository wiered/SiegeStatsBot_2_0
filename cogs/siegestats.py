from discord import ui
from discord.ext import commands

from cogs import ui as ui_cogs
from core import parser
from db.db import users_db


class SiegeStats(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
            
    @commands.command()
    async def stats(self,ctx, name:str=""):
        if not name:
            return await self.__get_self_stats__(ctx)
        return await self.__get_search_results__(ctx, name, auth=False)
        
    
    async def __get_search_results__(self, ctx, name, auth: bool = False):
        with parser.Parser() as p:
            search_results = p.search_player(name)
            embed = ui_cogs.SearchEmbed(search_results, name)
            view = ui_cogs.SearchButtonsView(search_results, name, auth)
            await ctx.send(embed=embed, view=view, delete_after=1800, ephemeral=True)
            await ctx.message.delete()
    
    
    async def __get_self_stats__(self, ctx):
        _user = users_db.get_user(ctx.author.id)
        if not _user or not _user._json:
            return await ctx.send(embed=ui_cogs.UnauthorizedEmbed())
        
        embed = ui_cogs.ProfileEmbed(_user.player_data, ctx.user.id)
        
        _view = ui.View()
        _view.add_item(ui_cogs.NoSeasonsSelect())
        _view = ui_cogs.SeasonsView(_user.player_data, ctx.user.id)
            
        return await ctx.send(embed=embed, view=_view)
            
    
    @commands.command()
    async def clear(self, ctx):
        await ctx.channel.clone(name = ctx.channel.name, reason = "Clearing channel")
        await ctx.channel.delete(reason = "Clearing channel")
    
    
async def setup(bot):
    await bot.add_cog(SiegeStats(bot))