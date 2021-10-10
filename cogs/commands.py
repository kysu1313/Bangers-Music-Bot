import discord
from discord.ext import commands
import time
from discord.utils import get
#from cogs.bot_parts.apis import Apis
from helpers.settings import Settings
from helpers.music import Music
import youtube_dl
#import youtube_dl

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()
        self.bot_id = self.settings.id
        self.client = discord.Client()

    # Events
    @commands.Cog.listener()
    async def on_ready(self,):
        print(f'{self.bot.user.name} has connected to Discord!')

    @commands.command(name='play', help='Plays music from youtube link')
    async def play(self, ctx, link):
        ms = Music(self.bot, commands.Context)
        await ctx.send(f"Playing {link}")
        
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        await ms.play_song(voice, link)
        await ctx.send("Done")

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    # Commands
    @commands.command(help='Simple check to verify bot is functioning properly')
    async def ping(self, ctx):
        await ctx.send('🏓 Pong!')

def setup(bot):
    bot.add_cog(Commands(bot))
