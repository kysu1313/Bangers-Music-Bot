
import asyncio
import discord
import youtube_dl
from discord.ext import commands

#
# References made to https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
#

class Music():

    def __init__(self, bot, ctx):
        self.yt_head = "https://www.youtube.com/"
        self.bot = bot
        self.ctx = ctx
        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = []

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()
        self.YTDL_OPTIONS = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }

        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        #self.audio_player = bot.loop.create_task(self.audio_player_task())

    def play_next_song(self, error=None):
        self.next.set()

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()
        if self.voice:
            await self.voice.disconnect()
            self.voice = None

    # !play https://www.youtube.com/watch?v=aIHF7u9Wwiw
    # !play https://www.youtube.com/watch?v=5gga8E43clk
    # !play https://www.youtube.com/watch?v=foE1mO2yM04
    async def play_song(self, voice, link):

        #FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        #YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True'}
        self.voice = voice
        #self.voice = discord.utils.get(self.bot.voice_clients, guild=self.ctx.guild)
        with youtube_dl.YoutubeDL(self.YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(link, download=False)
            I_URL = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(I_URL, **self.FFMPEG_OPTIONS)
            self.voice.play(source)
            self.voice.is_playing()

        #url = link
        #video = pafy.new(url)
        #best = video.getbest()
        #playurl = best.url

        #Instance = vlc.Instance()
        #player = Instance.media_player_new()
        #Media = Instance.media_new(
        #        playurl
        #        #"no-video-title"
        #        #"rtsp-tcp",
        #        #"network-caching=300",
        #        #"no-auto-adjust-pts-delay" # trying to prevent pts delay from increasing...
        #        )
        #Media.get_mrl()
        #player.set_media(Media)
        #player.play()

        while True:
                pass
                #if player.is_playing():
                #        pass
                #else:
                #        break


        print("working")

