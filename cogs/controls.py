
from discord.ext.commands import has_permissions
from helpers.settings import Settings
from discord.ext import commands
import discord

class Controls(commands.Cog):

    _slow_mode = False
    _slow_time = 15

    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()


    @has_permissions(administrator=True)
    @commands.command(name='slowmode', help='!slowmode <1-60 sec?> <on / off?>, enable / disable slowmode. Default time = 15 sec.')
    async def slowmode(self, ctx, enable=None, time=None):
        server_id =  ctx.message.guild.id
        conn = DbConn()
        if enable is None:
            enable = 0
        if time is None:
            time = 15
        conn.set_slow_mode(server_id, enable, time)
        await ctx.send("SlowMode set to {}".format(enable))

    async def getslowmode(self, server_id):
        conn = DbConn()
        enabled, time = conn.get_slow_mode(server_id)
        return enabled, time

def setup(bot):
    bot.add_cog(Controls(bot))
