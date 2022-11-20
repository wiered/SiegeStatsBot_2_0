from discord import app_commands
from discord.ext import commands
from discord import ui as ui_discord
from discord import app_commands, Interaction

from cogs import ui as ui_cogs
from core import parser
from db.db import users_db


class HubTree(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    
    @app_commands.command(name="stats", description="Get siege stats")
    async def stats(self,ctx, name:str=""):
        if not name:
            return await self.__get_self_stats__(ctx)
        return await self.__get_search_results__(ctx, name, auth=False, ephemeral=False)
    
    @app_commands.command(name="sielent_stats", description="Get siege stats. Will see only you")
    async def sielent_stats(self,ctx, name:str=""):
        if not name:
            return await self.__get_self_stats__(ctx, ephemeral=True)
        return await self.__get_search_results__(ctx, name, auth=False, ephemeral=True)
        
        
    @app_commands.command(name="authorize", description="Authorize your account")
    async def auth(self, interaction: Interaction, name: str) -> None:
        if not name or len(name) < 3:
            return await interaction.response.send_message("Please provide your name!")
        
        if interaction.user.id in users_db.keys:
            return await interaction.response.send_message(embed=ui_cogs.AuthorizedEmbed(), ephemeral=True)
        
        await self.__get_search_results__(interaction, name, auth=True, ephemeral=True)
        
    
    async def __get_search_results__(self, interaction: Interaction, name, auth: bool = False, ephemeral: bool = False):
        with parser.Parser() as p:
            search_results = p.search_player(name)
            embed = ui_cogs.SearchEmbed(search_results, name)
            view = ui_cogs.SearchButtonsView(search_results, interaction.user.id, auth)
            await interaction.response.send_message(embed=embed, view=view, delete_after=1800, ephemeral=ephemeral)
    
    
    async def __get_self_stats__(self, interaction: Interaction, ephemeral: bool = False):
        _user = users_db.get_user(interaction.user.id)
        if not _user:
            return await interaction.response.send_message(embed=ui_cogs.UnauthorizedEmbed(), ephemeral=ephemeral)
        
        embed = ui_cogs.ProfileEmbed(_user.player_data, interaction.user.id)
        
        _view = ui_discord.View()
        _view.add_item(ui_cogs.NoSeasonsSelect())
        _view = ui_cogs.SeasonsView(_user.player_data, interaction.user.id)
            
        return await interaction.response.send_message(embed=embed, view=_view, ephemeral=ephemeral)
        

async def setup(bot):
    await bot.add_cog(HubTree(bot))