import asyncio
import discord
from discord.ext import commands
from helpers.song_queue import SongQueue
from async_timeout import timeout
from helpers.ytld_helper import VoiceError

# Lots of this comes from vbe0201, https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d

class PlayState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self.ctx = ctx
        self.current = None
        self.next = asyncio.Event()
        self.song_queue = SongQueue()
        self.voice = None
        self._loop = False
        self._volume = 0.5

        self.player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def play_song(self):
        if not self.is_playing:
            await self.audio_player_task()
        else:
            self.is_playing = True

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                try:
                    #async with timeout(180):  # 3 minutes
                    self.current = await self.song_queue.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source)  # , after=self.play_next_song
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.song_queue.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None