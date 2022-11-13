__version__ = "0.0.1"

import asyncio
import logging
import logging.handlers
import os
import re

import discord
from discord import ui, Interaction
from discord.ext import commands
from discord import app_commands, Intents, Client, Interaction

import core
from cogs import siegestats
from config import Config
from core import parser
from core.models import (
    configure_logging,
    getLogger,
)
from core import user
from core import embed_generator
from core.console_out import cout
from core.json_unpacker import unpack_season_json
from core.models import ch
from db.db import users_db

__version__ = "2.0.0a"

# logger = getLogger(__name__)

temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

users_vault = user.UsersVault()
discord_version = "2.0.1"


class R6HubBot(commands.Bot):
    def __init__(self):
        intents = Intents.all()
        super().__init__(command_prefix="w!", intents=intents)
        
        self.config = Config()
        self.loaded_cogs = ["cogs.siegestats", "cogs.slash_commands"]
        self.start_time = discord.utils.utcnow()
        self.log_file_name = os.path.join(temp_dir, f"{self.start_time}_app.log")
        
        print("Bot is ready!")
        

    async def on_connect(self):
        # logger.debug("Connected to gateway.")
        await self.load_extensions()
        self.startup()
        try:
            synced = await bot.tree.sync()
            print(f"Synced: {synced}")
        except discord.HTTPException:
            print("Failed to sync application commands.")
        
        
    def startup(self):
        pass
        # logger.info("v%s", __version__)
        # logger.info("Authors: wrds")
        # logger.line()
        # logger.info("discord.py: v%s", discord.__version__)
        # logger.line()    
        
    async def load_extensions(self):
        for cog in self.loaded_cogs:
            if cog in self.extensions:
                continue
            try:
                await self.load_extension(cog)
            except Exception:
                pass
        print("Cogs are ready!")
    
    def _configure_logging(self):
        level_text = self.config.log_level.upper()
        logging_levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
        }
        # logger.line()

        log_level = logging_levels.get(level_text)
        if log_level is None:
            pass
            # log_level = self.config.remove("log_level")
            # logger.warning("Invalid logging level set: %s.", level_text)
            # logger.warning("Using default logging level: INFO.")
        else:
            pass
            # logger.info("Logging level: %s", level_text)

        # logger.info("Log file: %s", self.log_file_name)
        configure_logging(self.log_file_name, log_level)
        # logger.debug("Successfully configured logging.")
 
     
class AuthButton(ui.Button):
    def __init__(self, d_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__d_id = d_id
            
    
    async def callback(self, interaction: Interaction):
        _user = user.User(name = str(self.label), d_id = self.__d_id, siege_id=str(self.custom_id))
        users_db.add_user(_user)
        if interaction.message:
            _view = embed_generator.seasons_select(_user.full_json, self.__d_id, str(self.label), str(self.custom_id))
            await interaction.response.edit_message(
                content=f"Authorized as {_user.name}",
                embed=embed_generator.generate_player_embed(_user._json),
                view=_view
            )


class SearchButton(ui.Button):
    def __init__(self, d_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__d_id = d_id
            
    
    async def callback(self, interaction: Interaction):
        _user = user.User(name = str(self.label), d_id = self.__d_id, siege_id=str(self.custom_id))
        if interaction.message:
            _view = embed_generator.seasons_select(_user.full_json, self.__d_id, str(self.label), str(self.custom_id))
            await interaction.response.edit_message(
                content=f"Stats for {_user.name}",
                embed=embed_generator.generate_player_embed(_user._json),
                view=_view
            )
                

class SeasonSelect(ui.Select):
    def __init__(self, d_id: int, name, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__d_id = d_id
        self.__user_name = str(name)
        self.__user_id = user_id
        
    
    async def callback(self, interaction: Interaction):    
        if not interaction.message:
            return
        
        _user = user.User(name = self.__user_name, d_id = self.__d_id, siege_id=str(self.__user_id))
        if not _user:
            return
        
        season = self.values[0]
        full_json = _user.full_json
        if not(full_json or isinstance(full_json, dict)):
            return
        
        _json = unpack_season_json(full_json, int(season))
        embed = embed_generator.generate_past_season(_json)
        _view = embed_generator.seasons_select(_user.full_json, self.__d_id, self.__user_name, str(self.__user_id))
        if embed:
            await interaction.response.edit_message(
                embed=embed, 
                view=_view
            )
            
            
class FileFormatter(logging.Formatter):
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    def format(self, record):
        record.msg = self.ansi_escape.sub("", record.msg)
        return super().format(record)        

users_db.load_instance_from_csv()
config = Config()
bot = R6HubBot()

@bot.tree.command()
async def my_command(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Hello from my command!")
    

async def main():
    __setup_logger__()
    
    async with bot:
        bot.tree.copy_global_to(guild=discord.Object(id=993907879662866532))
        await bot.start(config.token)
        
    siegestats.save_db()

def __setup_logger__():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)   
    

if __name__ == "__main__":
    print(f"Global UsersVault: {users_vault}")
    asyncio.run(main())
    