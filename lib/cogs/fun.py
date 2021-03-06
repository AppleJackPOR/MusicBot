import asyncio
import os
from datetime import datetime

import discord
import youtube_dl
from discord import Embed
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Cog
from discord.ext.commands import command
from dotenv import load_dotenv

load_dotenv()

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '/music_files/%(id)s.mp3',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Fun(Cog, BotBase):
    def __init__(self, bot):
        self.bot = bot

    @command(name='play', aliases=['sing'])
    async def play(self, ctx, *, url):
        if ctx.message.author.voice is None:
            await ctx.send("Tão pinguim, tens de estar conectado a um voice channel")
        elif ctx.message.guild.voice_client is None:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('Now playing: {}'.format(player.title))
        elif ctx.message.guild.voice_client.channel == ctx.message.author.voice.channel:
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player)  # , after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('Now playing: {}'.format(player.title))
        else:
            await ctx.send("Zequinha, estou ocupado noutro canal a bombar uns sons mêmo à bacanz")

    @command(name='pause', aliase=['pausa'])
    async def pause(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.pause()

    @command(name='resume', aliases=['continuar'])
    async def resume(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.resume()

    @command(name="info", aliases=["inf"])
    async def show_info(self, ctx):
        embed = Embed(title="**DJ PaixHug - Music Bot**", description="",
                      colour=0x248BFF, timestamp=datetime.utcnow())
        fields = [("`Type`", "Music Bot", True),
                  ("`Prefix`", "%", True),
                  ("`Playing`", "Playlist do Hugo", False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_author(name="Gaming Nerds Bot - Padjojé & Hugo", icon_url=os.getenv('DAISY_IMG'))
        embed.set_footer(text="Bot em construção")
        embed.set_thumbnail(url=os.getenv('TROLL_IMG'))
        await ctx.send(embed=embed)

    @command(name="ping")
    async def send_ping(self, ctx):
        await ctx.send("pong")

    @command(name="join")
    async def join_voice(self, ctx):
        if ctx.message.author.voice is None:
            await ctx.send('You are not connected to a voice channel')
        elif ctx.message.guild.voice_client is not None:
            await ctx.send('Já estou conectado')
        else:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            await ctx.send(f"Conectado a: {channel}")

    @command(name="leave", aliases=["disconnect", "baza"])
    async def leave_voice(self, ctx):
        voice = ctx.message.guild.voice_client
        await voice.disconnect()
        await ctx.send('Bazei')

    @command(name="hello", aliases=["hi", "Hi", "Hello"])
    async def say_hello(self, ctx):
        # apaga a mensagem do user
        # await ctx.message.delete()
        await ctx.send(f"Olá {ctx.author.mention}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
