
import asyncio
import itertools
import random
import discord
import youtube_dl
from discord.ext import commands
from helpers.song_queue import SongQueue
from helpers.play_state import PlayState
from helpers.ytld_helper import YTDLSource


class Music():

    def __init__(self, bot, ctx, voice):
        self.yt_head = "https://www.youtube.com/"
        self.bot = bot
        self.ctx = ctx

        self.is_playing = False

        self.current = None
        self.voice = voice
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.voice_states = {}
        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.players = {}
        self.queues = {}
        
        #songs = asyncio.Queue()
        #play_next_song = asyncio.Event()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def get_voice_state(self, ctx: commands.Context):
        state = self.players.get(ctx.guild.id)
        if not state:
            #state = PlayState(self.bot, ctx)
            self.players[ctx.guild.id] = self.voice

        return state

    # !play https://www.youtube.com/watch?v=mzB1VGEGcSU
    # !play https://www.youtube.com/watch?v=aIHF7u9Wwiw
    # !play https://www.youtube.com/watch?v=5gga8E43clk
    # !play https://www.youtube.com/watch?v=foE1mO2yM04

    def play_next_song(self, error=None):
        self.next.set()

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing:
            self.voice.stop()
        self.play_next_song()

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    async def add_song(self, song):
        await self.songs.put(song)

    async def stop(self):
        if self.voice.is_playing:
            await self.voice.stop()

    async def pause(self):
        if self.is_playing:
            await self.voice.pause()

    async def resume(self):
        if not self.is_playing:
            self.play_next_song()            

    async def audio_player_task(self):
        while True:
            self.is_playing = False
            self.next.clear()
            if not self._loop:
                try:
                    #async with timeout(180):  # 3 minutes
                    self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)  # , after=self.play_next_song
            self.is_playing = True
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    #async def audio_player_task(self):
    #    while True:
    #        self.next.clear()
    #        current = await self.songs.get()
    #        if current is not None:
    #            #current.start()
    #            self.is_playing = True
    #            self.voice.play(current.source)
    #            print(self.songs.qsize())
    #            #await self.ctx.send(current.build_embed())
    #        await self.next.wait()

    def toggle_next(self):
        self.ctx.loop.call_soon_threadsafe(self.next.set)

    def check_queue(self, id):
        if self.queues[id] != []:
            player = self.queues[id].pop(0)
            self.players[id] = player
            player.start()

    # !play https://www.youtube.com/watch?v=aIHF7u9Wwiw
    # !play https://www.youtube.com/watch?v=5gga8E43clk
    # !play https://www.youtube.com/watch?v=foE1mO2yM04


