import asyncio
import atexit

import discord
from discord.ext import commands
from discord import Intents

from config import Config
from db.db import users_db

__version__ = "2.0.2"


class R6HubBot(commands.Bot):
    def __init__(self):
        intents = Intents.all()
        super().__init__(command_prefix="w!", intents=intents)
        
        self.config = Config()
        self.loaded_cogs = ["cogs.siegestats", "cogs.slash_commands"]
        self.start_time = discord.utils.utcnow()
        
        print("Bot is ready!")
        

    async def on_connect(self):
        await self.load_extensions()
        try:
            synced = await bot.tree.sync()
            print(f"Synced: {synced}")
        except discord.HTTPException:
            print("Failed to sync application commands.")
         
        
    async def load_extensions(self):
        for cog in self.loaded_cogs:
            if cog in self.extensions:
                continue
            try:
                await self.load_extension(cog)
            except Exception:
                pass
            

users_db.load_instance_from_csv()
config = Config()
bot = R6HubBot()


async def main():
    users_db.load_instance_from_csv()
    
    async with bot:
        bot.tree.copy_global_to(guild=discord.Object(id=993907879662866532))
        await bot.start(config.token)


def exit_handler():
    users_db.save_instance_to_csv()
    print("Bot is shutting down!")


if __name__ == "__main__":
    atexit.register(exit_handler)
    asyncio.run(main())