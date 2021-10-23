import asyncio
import random
import discord
from discord import client
from discord.ext import commands
import time
import humanize
from datetime import datetime as dt
import datetime
from discord.utils import get
from helpers.saver import PlaylistSaver
from helpers.settings import Settings
from helpers.music import Music
from helpers.song import Song
from helpers.ytld_helper import VoiceError, YTDLError, YTDLSource
import typing as t

#client = discord.Client()
PLAYLIST_PREFIXES = ['-playlist', '-plst', '-p', '-pl']

class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class AudioPlayError(commands.CommandError):
    pass

class ClearQueueError(commands.CommandError):
    pass

class SkipSongError(commands.CommandError):
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

        self.curr_plst_pg = {}
        self.voice_states = {}
        self.curr_playlists = {}
        self.last_playlist_shown = {}
        self.curr_ctx = {}

    def get_voice_state(self, ctx: commands.Context):
        try:
            state = self.voice_states.get(ctx.guild.id)
            if not state:
                state = Music(self.bot, ctx, self.voice)
                self.voice_states[ctx.guild.id] = state

            return state
        except Exception as e:
            raise NoVoiceChannel("Unable to get current voice state.")

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
        try:
            server = ctx.author.voice.channel
            if ctx.voice_state.voice:
                await ctx.voice_state.voice.move_to(server)
                return
            ctx.voice_state.voice = await server.connect()
            self.voice_states[server.id] = ctx.voice_state
        except Exception as e:
            pass

    @commands.command(name='play', help='Plays music from youtube link or playlist <!play -playlist>')
    async def play(self, ctx: commands.Context, *link):
        try:
            if not ctx.voice_state.voice:
                channel = ctx.author.voice.channel
                await ctx.send('Must invite bot to voice channel first. (Adding the bot to your channel now)')
                await ctx.invoke(self.join, channel=channel)
            
            #self.voice_state[ctx.guild.id] = ctx.voice_state
            self.curr_playlists[ctx.guild.id] = "--NONE--"
            shuffle = False
            if link[0] in PLAYLIST_PREFIXES:
                #link = link.split()
                if '-shuffle' in str(link):
                    link.pop(link.index('-shuffle'))
                    shuffle = True
                shuffle = (True if '-shuffle' in str(link) else False)
                saver = PlaylistSaver()
                user = ctx.author
                if len(link) >= 2:
                    user_songs = saver._get_plist(" ".join(link[1:]), user.id)
                else:
                    user_songs = saver.get_songs(user)
                if len(user_songs) > 0:
                    ctx.playlist = " ".join(link[1:])
                    self.curr_playlists[ctx.guild.id] = " ".join(link[1:])
                    if shuffle:
                        random.shuffle(user_songs)
                    await ctx.send('''loading playlist''')
                    for s in user_songs:
                        async with ctx.typing():
                            try:
                                source = await YTDLSource.create_source(ctx, str(s[2]), loop=self.bot.loop)
                            except YTDLError as e:
                                return await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                            else:
                                song = Song(source, str(s[2]))
                                queue_pos = ctx.voice_state.songs._unfinished_tasks
                                await ctx.voice_state.songs.put((queue_pos+1, song))
                    return await ctx.send('''Enqueued {}'s playlist'''.format(user.name))
                return await ctx.send("You haven't liked any songs yet.")
            else:
                async with ctx.typing():
                    try:
                        source = await YTDLSource.create_source(ctx, str(link), loop=self.bot.loop)
                    except YTDLError as e:
                        return await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                    else:
                        song = Song(source, str(link))
                        queue_pos = ctx.voice_state.songs._unfinished_tasks
                        await ctx.voice_state.songs.put((queue_pos+1, song))
                        return await ctx.send('Enqueued {}'.format(str(source)))
        except Exception as e:
            raise AudioPlayError(f"Something went wrong: {e}")

    async def _play_song(self, idx: int, ctx: commands.Context):
        """ 
        Play a song by reacting to the !playlist command. 
        Automatically places the song to play next in the queue.
         """
        try:
            saver = PlaylistSaver()
            curr = self.last_playlist_shown[ctx.guild.id]
            curr_ctx = self.curr_ctx[ctx.guild.id]
            song_name = curr.split('.')[0]
            uid = curr.split('.')[1]
            curr_playlist = saver._get_plist(song_name, uid)
            sng = curr_playlist[idx + 1]
            song = None
            try:
                source = await YTDLSource.create_source(curr_ctx, str(sng[2]), loop=self.bot.loop)
            except YTDLError as e:
                return await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                song = Song(source, str(sng[2]))
            voice = self.voice_states[ctx.guild.id]
            #queue_pos = voice.songs.__len__()
            await voice.songs.put((0, song))
        except Exception as e:
            print(e)
            pass

    #@play.after_invoke
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, ctx):
        if not ctx.bot:
            emoji = str(reaction.emoji)
            voice = self.voice_states[ctx.guild.id]
            
            reacts = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟',]
            if emoji in reacts:
                idx = reacts.index(emoji)
                await self._play_song(idx, ctx)
            
            if emoji == '⏯':
                if voice.is_playing:
                    voice.pause()
            if emoji == '⏹':
                voice.stop()
            if emoji == '⏩':
                voice.skip()
            if emoji == '❤️':
                await self.reaction_save(reaction.message.author, ctx, playlist=None)
            if emoji == '🔀':
                await self.shuffle(ctx)
            if emoji == '🔂':
                await self.repeat(ctx)
            if emoji == '⬅️':
                await self.songs(ctx, self.last_playlist_shown[ctx.guild.id], self.curr_plst_pg[ctx.guild.id]-1)
            if emoji == '➡️':
                await self.songs(ctx, self.last_playlist_shown[ctx.guild.id], self.curr_plst_pg[ctx.guild.id]+1)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, ctx):
        if not ctx.bot:     #checks if message is from bot
            emoji = str(reaction.emoji)
            voice = self.voice_states[ctx.guild.id]
            if emoji == '⏯':
                if voice.is_playing:
                    voice.resume()

    @commands.command(name='clear', aliases=['empty'])
    async def clear(self, ctx):
        try:
            if not ctx.voice_state.voice:
                channel = ctx.author.voice.channel
                await ctx.send('You are not currently in a voice channel so you cant clear a playlist.')
                return
            ctx.voice_state.stop()
            ctx.voice_state.songs.clear()
            await ctx.send("Playlist cleared")
        except Exception as e:
            raise ClearQueueError(f"Unable to clear current queue {e}")

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        #await ctx.voice_client.cleanup()

    @commands.command(name='skip')
    @commands.has_permissions(manage_guild=True)
    async def _skip(self, ctx: commands.Context):
        """Skips the currently playing song."""

        try:
            if not ctx.voice_state.is_playing:
                return await ctx.send('Not playing any music right now...')
            else:
                ctx.voice_state.skip()
        except Exception as e:
            raise SkipSongError(f"Unable to skip the currently playing song: {e}")

    @commands.command(name='loop')
    @commands.has_permissions(manage_guild=True)
    async def loop(self, ctx: commands.Context):
        """Pauses the currently playing song."""
        try:
            if ctx.voice_state.is_playing:
                ctx.voice_state.loop(not ctx.voice_state.loop)
        except Exception as e:
            await ctx.send(f"Error pausing track: {e}")
            pass

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""
        try:
            if ctx.voice_state.is_playing:
                ctx.voice_state.pause()
        except Exception as e:
            await ctx.send(f"Error pausing track: {e}")
            pass

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""
        try:
            if ctx.voice_state.voice.is_paused():
                ctx.voice_state.resume()
        except Exception as e:
            await ctx.send(f"Error resuming track: {e}")
            pass

    @commands.command(name='stop')
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        try:
            ctx.voice_state.songs.clear()
            if not ctx.voice_state.is_playing:
                await ctx.voice_state.stop()
        except Exception as e:
            await ctx.send(f"Error stopping track: {e}")
            pass

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player."""

        try:
            if 0 > volume > 100:
                return await ctx.send('Volume must be between 0 and 100')
            ctx.voice_state.volume = volume / 100
            await ctx.send('Volume of the player set to {}%'.format(volume))
        except Exception as e:
            await ctx.send(f"Error setting volume: {e}")
            pass

    @commands.command(name='now', aliases=['show', 'current'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song and future playlist if it exists."""

        try:
            sng = ctx.voice_state.current[1]
            embed = sng.build_embed()
            embed.add_field(name='Current Playlist:\n', value='------------', inline=False)
            count = 1
            for song in ctx.voice_state.songs.__iter__():
                embed.add_field(name=f'{count}): {song.name}', value=f'[Click]({song.link})', inline=False)
                count += 1
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error showing current tracks: {e}")
            pass

    @commands.command(name='save', aliases=['like', 'favorite'])
    async def save(self, ctx: commands.Context, playlist=None):
        """Saves the currently playing song to user playlist."""

        try:
            saver = PlaylistSaver()
            user = ctx.author
            song = ctx.voice_state.current[1]
            if playlist is not None:
                result = saver.add_to_playlist(playlist, user, song)
                if result is None:
                    return await ctx.send(f"Failed to save song to playlist {playlist}")
            else:
                result = saver.add_to_playlist('likes', user, song)
                if result is None:
                    return await ctx.send("Failed to like song")
            await ctx.send("{} - Saved {}".format(user.name, song.name))
        except Exception as e:
            await ctx.send(f"Error saving current song: {e}")
            pass

    async def reaction_save(self, user, ctx: commands.Context, playlist=None):
        """Saves the currently playing song to user playlist."""

        try:
            saver = PlaylistSaver()
            #user = ctx.author
            song = ctx.voice_state.current[1]
            if playlist is not None:
                result = saver.add_to_playlist(playlist, user, song)
                if result is None:
                    return await ctx.send(f"Failed to save song to playlist {playlist}")
            else:
                result = saver.add_to_playlist('likes', user, song)
                if result is None:
                    return await ctx.send("Failed to like song")
            await ctx.send("{} - Saved {}".format(user.name, song.name))
        except Exception as e:
            await ctx.send(f"Error saving current song: {e}")
            pass

    @commands.command(name='playlist', aliases=['mysongs', 'songs', 'liked', 'favorites', 'likes'])
    async def songs(self, ctx: commands.Context, playlist=None, page=1):
        """Displays a users playlist."""

        try:
            self.curr_ctx[ctx.guild.id] = ctx
            self.curr_plst_pg[ctx.guild.id] = page
            pg_size = 10
            saver = PlaylistSaver()
            user = ctx.author
            if playlist is not None:
                user_songs = saver._get_plist(playlist, user.id)
                if user_songs == None:
                    await ctx.send("That playlist doesn't exist.")
                    all_plsts = saver._get_all_plists(user)
                    if all_plsts == None:
                        return await ctx.send("You don't have any playlists. Use '!makeplaylist <playlist-name>' to create one.")
                    else:
                        return ctx.send(embed=self._create_embed(user, 'Playlists', all_plsts)) 
            else: 
                user_songs = saver.get_songs(user)
            self.last_playlist_shown[ctx.guild.id] = (playlist if playlist is not None else "likes")+"."+str(ctx.author.id)
            embed = discord.Embed(title=f'''{user.name}'s {'playlist' if playlist is None else playlist} (Page: {page})''',
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
            reacts = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
            for i in range(1, count):
                await msg.add_reaction(reacts[i-1])
            #if count >= 1:
            #    await msg.add_reaction('⬅️')
            #    await msg.add_reaction('➡️')
        except Exception as e:
            await ctx.send(f"Error displaying playlist: {e}")
            pass

    @commands.command(name='playlists', aliases=['myplaylists', 'mylists', 'plsts'])
    async def playlists(self, ctx: commands.Context):
        """Displays a users playlists."""

        try:
            saver = PlaylistSaver()
            user = ctx.author
            all_plsts = saver._get_all_plists(user)
            if all_plsts == None:
                return await ctx.send("You don't have any playlists. Use '!makeplaylist <playlist-name>' to create one.")
            else:
                return await ctx.send(embed=self._create_playlist_embed(user, 'Playlists', all_plsts)) 
        except Exception as e:
            await ctx.send(f"Error displaying playlist: {e}")
            pass

    def _create_playlist_embed(self, user, title, text):
        embed = discord.Embed(title=f'''{user.name}'s {title}''',
                               color=discord.Color.blurple())
        count = 0
        for i in text:
            count += 1
            #dt_obj = dt.strptime(i[3],'%Y-%m-%d %H:%M:%S.%f')
            xdt = dt.strptime(i[3],'%Y-%m-%d %H:%M:%S.%f').replace(microsecond=0)
            days = humanize.naturaldate(datetime.date(xdt.year, xdt.month, xdt.day))
            embed.add_field(name=f'{count}): {i[1]}', value=f' Date Created: {days}', inline=False)
        return embed

    def _create_embed(self, user, title, text):
        embed = discord.Embed(title=f'''{user.name}'s {title}''',
                               color=discord.Color.blurple())
        count = 0
        for i in text:
            count += 1
            embed.add_field(name=f'{count}): ', value=f' {i}', inline=False)
        return embed

    @commands.command(name='makeplaylist', aliases=['newplaylist', 'createlist', 'createplaylist'])
    async def makeplaylist(self, ctx: commands.Context, playlist_name):
        """Creates new plalist."""

        try:
            saver = PlaylistSaver()
            user = ctx.author
            res, err = saver.create_playlist(playlist_name, user)
            if res is False:
                return await ctx.send(f"You already have a playlist named {playlist_name}")
            elif res is None:
                return await ctx.send(f"Error: {err}")
            return await ctx.send("{} - Created playlist {}".format(user.name, playlist_name))
        except Exception as e:
            await ctx.send(f"Error creating playlist: {e}")
            pass

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
