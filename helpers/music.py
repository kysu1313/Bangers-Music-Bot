import asyncio
from helpers.song_queue import SongQueue

# Huge props goes to vbe0201 https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
# For help and inspiration

class Music():

    def __init__(self, bot, ctx, voice):
        self.bot = bot
        self.ctx = ctx

        #self.is_playing = False

        self.current = None
        self.voice = voice
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.voice_states = {}
        self._loop = False
        self._volume = 0.5
        #self.volume = self._volume
        self.skip_votes = set()

        self.players = {}
        self.queues = {}

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    # TEST SONGS
    # !play https://www.youtube.com/watch?v=mzB1VGEGcSU
    # !play https://www.youtube.com/watch?v=aIHF7u9Wwiw
    # !play https://www.youtube.com/watch?v=5gga8E43clk
    # !play https://www.youtube.com/watch?v=foE1mO2yM04

    def get_current(self):
        return self.current

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def add_song(self, song):
        await self.songs.put(song)

    def skip(self):
        self._stop()

    def _stop(self):
        if self.voice.is_playing:
            self.voice.stop()

    def pause(self):
        self.voice.pause()

    def resume(self):
        if not self.is_playing:
            self.play_next_song()   
        else:
            self.voice.resume() 

    def play_next_song(self, error=None):
        self.next.set()        

    async def audio_player_task(self):
        while True:
            self.next.clear()
            if not self._loop:
                try:
                    self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.add_reactions()

            await self.next.wait()

    async def add_reactions(self):
        msg = await self.current.source.channel.send(embed=self.current.build_embed())
        await msg.add_reaction('▶️')
        await msg.add_reaction('⏯')
        await msg.add_reaction('⏩')
        await msg.add_reaction('⏹')

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


