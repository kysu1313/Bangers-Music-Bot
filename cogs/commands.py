import asyncio
import discord
from discord import client
from discord.ext import commands
import time
from discord.utils import get
from helpers.settings import Settings
from helpers.music import Music
from helpers.song import Song
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
        server = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(server)
            return
        ctx.voice_state.voice = await server.connect()

        try:
            await self.bot.wait_for('reaction_add', check=self.check)
        except asyncio.TimeoutError:
            pass

    #@commands.command(name='test')
    #async def test(self, ctx):
    #    current = ctx.voice_state.get_current()
    #    embed = current.build_embed()
    #    await current.source.channel.send(embed = embed)


    def check(self, reaction, ctx):
        result = asyncio.create_task(self.run_check(reaction, ctx)) # run the async function
        return result

    async def run_check(self, reaction, ctx):
        emoji = str(reaction.emoji)
        if emoji == '⏯': # and ctx.user != self.bot.user:
            if ctx.voice_state.is_playing:
                await ctx.voice_state.pause()
            else:
                await ctx.voice_state.resume()
        if emoji == '⏹': # and ctx.user != self.bot.user:
            await ctx.voice_state.stop()
        if emoji == '⏩': # and ctx.user != self.bot.user:
            await ctx.voice_state.skip()

    @commands.command(name='play', help='Plays music from youtube link')
    async def play(self, ctx: commands.Context, *link):
        
        if not ctx.voice_state.voice:
            await ctx.invoke(self.join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, str(link), loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                song = Song(source, str(link))

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {}'.format(str(source)))

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        #await ctx.voice_client.cleanup()

    @commands.command(name='skip')
    @commands.has_permissions(manage_guild=True)
    async def _skip(self, ctx: commands.Context):
        """Skips the currently playing song."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')
        else:
            await ctx.voice_state.skip()

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if ctx.voice_state.is_playing:
            await ctx.voice_state.pause()

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            await ctx.voice_state.resume()

    @commands.command(name='stop')
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if not ctx.voice_state.is_playing:
            await ctx.voice_state.stop()

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player."""

        #if not self.music.is_playing:
        #    return await ctx.send('Nothing being played at the moment.')

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')

        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

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
        
        #if self.music is None:
        #    self.music = Music(self.bot, commands.Context, self.voice)

    # Commands
    @commands.command(help='Simple check to verify bot is functioning properly')
    async def ping(self, ctx):
        await ctx.send('🏓 Pong!')

def setup(bot):
    bot.add_cog(Commands(bot, client))
