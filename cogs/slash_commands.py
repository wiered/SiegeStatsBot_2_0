import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
from discord import app_commands, Intents, Client, Interaction


from core import parser
from core import embed_generator
from core.embed_generator import StdEmbeds
from db.db import users_db


class HubTree(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    
    @app_commands.command(name="stats", description="Get siege stats")
    async def stats(self,ctx, name:str=""):
        print("Searching user in: ", users_db.users)
        if not name:
            return await self.__get_self_stats__(ctx)
        return await self.__get_search_results__(ctx, name, auth=False)
        
        
    @app_commands.command(name="authorize", description="Authorize your account")
    async def auth(self, interaction: Interaction, name: str) -> None:
        print(name)
        
        if not name or len(name) < 3:
            return await interaction.response.send_message("Please provide your name!")
        
        if interaction.user.id in users_db.keys:
            return await interaction.response.send_message(embed=StdEmbeds().authorized_embed())
        
        await self.__get_search_results__(interaction, name, auth=True)
        
    
    async def __get_search_results__(self, interaction: Interaction, name, auth: bool = False):
        with parser.Parser() as p:
            search_results = p.search_player(name)
            embed = embed_generator.generate_search_embed(search_results, name)
            view = embed_generator.generate_buttons(search_results, interaction.user.id, auth=auth)
            await interaction.response.send_message(embed=embed, view=view, delete_after=1800)
            # await interaction.message.delete()
    
    
    async def __get_self_stats__(self, interaction):
        _user = users_db.get_user(interaction.user.id)
        if _user and _user._json:
            embed = embed_generator.generate_player_embed(_user._json)
            _view = ui.View()
            _view.add_item(StdEmbeds().no_seasons_select())
            
            if not _user._json.get("is_full"):
                return await interaction.response.send_message(embed=embed, view=_view)
            
            if _user.full_json:
                _view = embed_generator.seasons_select(_user.full_json, interaction.user.id, _user.name, _user.siege_id)
            return await interaction.response.send_message(embed=embed, view=_view)

    
    @commands.command()
    async def tsttree(self, ctx):
        await ctx.send("Test tree")  

async def setup(bot):
    await bot.add_cog(HubTree(bot))