from discord.ext import commands
from discord.ext import tasks

from core.data import RoleDicts
from db.db import users_db


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_roles.start()
        self.save_db.start()
    
    
    def cog_unload(self):
        self.update_roles.cancel()
    
    
    @tasks.loop(hours=1)
    async def update_roles(self):
        print("Updating roles...")
        for user in list(users_db.users.values()):
            guild = self.bot.get_guild(843082437961318400)
            member = guild.get_member(user.d_id)
            if not member: continue
            
            user.parse_data()
            
            role_id = RoleDicts.rank_roles.get(user.data.rank)
            role = guild.get_role(role_id)
            if role in member.roles: continue
            
            for _role in member.roles:
                if _role.id in RoleDicts.rank_roles_ids:
                    await member.remove_roles(_role)
                    
            await member.add_roles(role)
        print("Roles updated.")
            
    
    @tasks.loop(hours=6)
    async def save_db(self):
        print("Saving db...")
        users_db.save_instance_to_csv()
            
    
    @update_roles.before_loop
    async def update_roles_before(self):
        print("Waiting for bot to be ready...")
        await self.bot.wait_until_ready()
        

async def setup(bot):
    await bot.add_cog(RoleManager(bot))
    