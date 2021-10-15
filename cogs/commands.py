import asyncio
import random
import discord
from discord import client
from discord.ext import commands
import time
from discord.utils import get
from helpers.saver import PlaylistSaver
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

    def check(self, reaction, ctx):
        result = asyncio.create_task(self.run_check(reaction, ctx)) # run the async function
        return result

    async def run_check(self, reaction, ctx):
        emoji = str(reaction.emoji)
        if emoji == '⏯': # and ctx.user != self.bot.user:
            if ctx.voice_state.is_playing:
                ctx.voice_state.pause()
            else:
                ctx.voice_state.resume()
        if emoji == '⏹': # and ctx.user != self.bot.user:
            ctx.voice_state.stop()
        if emoji == '⏩': # and ctx.user != self.bot.user:
            ctx.voice_state.skip()

    @commands.command(name='play', help='Plays music from youtube link or playlist <!play -playlist>')
    async def play(self, ctx: commands.Context, *link):
        
        if not ctx.voice_state.voice:
            channel = ctx.author.voice.channel
            await ctx.send('Must invite bot to voice channel first. (Adding the bot to your channel now)')
            await ctx.invoke(self.join, channel=channel)

        if link[0] == '-playlist':
            saver = PlaylistSaver()
            user = ctx.author
            user_songs = saver.get_songs(user)
            if len(user_songs) > 0:
                if '-shuffle' in str(link):
                    random.shuffle(user_songs)
                await ctx.send('''loading playlist''')
                for s in user_songs:
                    async with ctx.typing():
                        try:
                            source = await YTDLSource.create_source(ctx, str(s[2]), loop=self.bot.loop)
                        except YTDLError as e:
                            await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                        else:
                            song = Song(source, str(s[2]))

                            await ctx.voice_state.songs.put(song)
                await ctx.send('''Enqueued {}'s playlist'''.format(user.name))
        else:
            async with ctx.typing():
                try:
                    source = await YTDLSource.create_source(ctx, str(link), loop=self.bot.loop)
                except YTDLError as e:
                    await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                else:
                    song = Song(source, str(link))

                    await ctx.voice_state.songs.put(song)
                    await ctx.send('Enqueued {}'.format(str(source)))

    @commands.command(name='clear', aliases=['empty'])
    async def clear(self, ctx):
        if not ctx.voice_state.voice:
            channel = ctx.author.voice.channel
            await ctx.send('You are not currently in a voice channel so you cant clear a playlist.')
            return
        ctx.voice_state.stop()
        ctx.voice_state.songs.clear()
        await ctx.send("Playlist cleared")

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
            ctx.voice_state.skip()

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if ctx.voice_state.is_playing:
            ctx.voice_state.pause()

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if ctx.voice_state.voice.is_paused():
            ctx.voice_state.resume()

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

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')
        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['show', 'current'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song and future playlist if it exists."""

        embed = ctx.voice_state.current.build_embed()
        embed.add_field(name='Current Playlist:\n', value='------------', inline=False)
        count = 1
        for song in ctx.voice_state.songs.__iter__():
            embed.add_field(name=f'{count}): {song.name}', value=f'[Click]({song.link})', inline=False)
            count += 1
        await ctx.send(embed=embed)

    @commands.command(name='save', aliases=['like', 'favorite'])
    async def save(self, ctx: commands.Context, playlist=None):
        """Saves the currently playing song to user playlist."""

        saver = PlaylistSaver()
        user = ctx.author
        song = ctx.voice_state.current
        if playlist is not None:
            result = saver.add_to_playlist(playlist, user, song)
        else:
            result = saver.save_song(user, song)
        await ctx.send("{} - Saved {}".format(user.name, song.name))

    @commands.command(name='playlist', aliases=['mysongs', 'songs', 'liked', 'favorites'])
    async def songs(self, ctx: commands.Context, page=1):
        """Displays a users playlist."""

        pg_size = 10
        saver = PlaylistSaver()
        user = ctx.author
        user_songs = saver.get_songs(user)
        embed = discord.Embed(title=f'''{user.name}'s playlist (Page: {page})''',
                               color=discord.Color.blurple())
        songs_to_show = []
        window = page*pg_size
        if window > len(user_songs):
            songs_to_show = user_songs[-pg_size:]
        else:
            songs_to_show = user_songs[window-10:window]
        count = 1
        for song in songs_to_show:
            embed.add_field(name=f'{count}): {song[1]}', value=f'[Click]({song[2]})', inline=False)
            count += 1
        msg = await ctx.send(embed=embed)
        reacts = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟',]
        for i in range(1, count):
            await msg.add_reaction(reacts[i-1])

    @commands.command(name='makeplaylist', aliases=['newplaylist', 'createlist', 'createplaylist'])
    async def makeplaylist(self, ctx: commands.Context, playlist_name):
        """Saves the currently playing song to user playlist."""

        saver = PlaylistSaver()
        user = ctx.author
        saver.create_playlist(playlist_name, user)
        await ctx.send("{} - Created playlist {}".format(user.name, playlist_name))

    @join.before_invoke
    @play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        """Verify everything is setup before playing or joining a voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')
        if self.voice is None:
            self.voice = discord.utils.get(self.bot.voice_clients, guild=commands.Context.guild)

    # Commands
    @commands.command(help='Simple check to verify bot is functioning properly')
    async def ping(self, ctx):
        await ctx.send('🏓 Pong!')

def setup(bot):
    bot.add_cog(Commands(bot, client))
