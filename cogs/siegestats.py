import discord
from discord import ui
from discord.ext import commands


from core import parser
from core import embed_generator
from core.user import UsersVault
from core.embed_generator import StdEmbeds

from db.db import users_db




def load_db():
    users_db.load_instance_from_csv()

def save_db():
    users_db.save_instance_to_csv()


class SiegeStats(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def auth(self, ctx, name):
        if not name or len(name) < 3:
            return await ctx.send("Please provide your name!")
        
        if ctx.author.id in users_db.keys:
            return await ctx.send(embed=StdEmbeds().authorized_embed())
        
        await self.__get_search_results__(ctx, name, auth=True)

            
    @commands.command()
    async def stats(self,ctx, name:str=""):
        print("Searching user in: ", users_db.users)
        if not name:
            return await self.__get_self_stats__(ctx)
        return await self.__get_search_results__(ctx, name, auth=False)
        

    
    async def __get_search_results__(self, ctx, name, auth: bool = False):
        with parser.Parser() as p:
            search_results = p.search_player(name)
            embed = embed_generator.generate_search_embed(search_results, name)
            view = embed_generator.generate_buttons(search_results, ctx.author.id, auth=auth)
            await ctx.send(embed=embed, view=view, delete_after=1800)
            await ctx.message.delete()
    
    
    async def __get_self_stats__(self, ctx):
        _user = users_db.get_user(ctx.author.id)
        if _user and _user._json:
            embed = embed_generator.generate_player_embed(_user._json)
            _view = ui.View()
            _view.add_item(StdEmbeds().no_seasons_select())
            
            if not _user._json.get("is_full"):
                return await ctx.send(embed=embed, view=_view)
            
            if _user.full_json:
                _view = embed_generator.seasons_select(_user.full_json, ctx.author.id, _user.name, _user.siege_id)
            return await ctx.send(embed=embed, view=_view)
        return await ctx.send(embed=StdEmbeds().not_authorized_embed())
            
    
    @commands.command()
    async def clear(self, ctx):
        await ctx.channel.clone(name = ctx.channel.name, reason = "Clearing channel")
        await ctx.channel.delete(reason = "Clearing channel")
    
    
async def setup(bot):
    await bot.add_cog(SiegeStats(bot))