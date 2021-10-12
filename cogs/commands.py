import asyncio
import discord
from discord import client
from discord.ext import commands
import time
from discord.utils import get
from helpers.settings import Settings
from helpers.music import Music
from helpers.song import Song
from helpers.play_state import PlayState
from helpers.ytld_helper import YTDLError, YTDLSource
import typing as t

#client = discord.Client()

class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class Commands(commands.Cog):
    def __init__(self, bot, client):
        self.bot = bot
        self.settings = Settings()
        self.bot_id = self.settings.id
        self.client = client
        #self.voice_state = PlayState(bot, commands.Context)
        self.music = None
        self.voice = None
        self.voice_client = None
        self.v_client = None
        
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = Music(self.bot, ctx, self.voice)
            self.voice_states[ctx.guild.id] = state

        return state

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    
    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    # Events
    @commands.Cog.listener()
    async def on_ready(self,):
        print(f'{self.bot.user.name} has connected to Discord!')

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', help='Join voice channel')
    async def join(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

        #channel = ctx.message.author.voice.channel
        #self.voice = await channel.connect(timeout=1000)
        #self.music = Music(self.bot, commands.Context, self.voice)

    @commands.command(name='play', help='Plays music from youtube link')
    async def play(self, ctx: commands.Context, *link):
        
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, str(link), loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                song = Song(source, str(link))

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {}'.format(str(source)))

        #source = await YTDLSource.create_source(ctx, str(link), loop=self.bot.loop)
        #song = Song(source, str(link))
        #await self.music.add_song(song)
        #await ctx.send('Enqueued {}'.format(str(source)))

        
        ##self.player = self.voice.create_ytdl_player(link)
        
        #await ctx.message.add_reaction('▶️')
        #await ctx.message.add_reaction('⏯')
        #await ctx.message.add_reaction('⏩')
        #await ctx.message.add_reaction('⏹')

        #try:
        #    # Timeout parameter is optional but sometimes can be useful
        #    await self.bot.wait_for('reaction_add', check=self.check)
        #except asyncio.TimeoutError:
        #    pass

    @commands.command(name='test')
    async def test(self, ctx):
        await self.music.pause()

    def check(self, reaction, user):
        result = asyncio.create_task(self.run_check(reaction, user)) # run the async function
        return result

    async def run_check(self, reaction, user):
        emoji = str(reaction.emoji)
        if emoji == '⏯' and user != self.bot.user:
            await self.music.pause()
        if emoji == '⏹' and user != self.bot.user:
            await self.music.stop()
        if emoji == '▶️' and user != self.bot.user:
            await self.music.resume()
        if emoji == '⏩' and user != self.bot.user:
            await self.music.skip()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        #await ctx.voice_client.cleanup()

    @commands.command(name='skip')
    @commands.has_permissions(manage_guild=True)
    async def _skip(self, ctx: commands.Context):
        """Skips the currently playing song."""

        if self.music.is_playing:
            self.music.skip()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            self.music.pause()
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

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player."""

        #if not self.music.is_playing:
        #    return await ctx.send('Nothing being played at the moment.')

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')

        self.music.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @join.before_invoke
    @play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

        if self.voice is None:
            self.voice = discord.utils.get(self.bot.voice_clients, guild=commands.Context.guild)
        
        if self.music is None:
            self.music = Music(self.bot, commands.Context, self.voice)

    # Commands
    @commands.command(help='Simple check to verify bot is functioning properly')
    async def ping(self, ctx):
        await ctx.send('🏓 Pong!')

def setup(bot):
    bot.add_cog(Commands(bot, client))
