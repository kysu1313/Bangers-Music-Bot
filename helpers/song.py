
import discord
from helpers.ytld_helper import YTDLSource

# Huge props goes to vbe0201 https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
# For help and inspiration

class Song:
    def __init__(self, source: YTDLSource, link: None):
        self.source = source
        self.name = source.title
        self.link = link
        self.requester = source.requester

    def build_embed(self):
        bg_clr = str("""```css\nbackground-color: #054162```""")
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed

