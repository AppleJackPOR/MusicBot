import datetime
import os
from asyncio import sleep
from glob import glob
from random import choice

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

load_dotenv()
PREFIX = "%"
OWNER_ID = os.getenv('OWNER_ID')
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

status_list = ["Super Mario", "CS:GO", "Alone"]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print("cog loaded")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_ID,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("Setup completed")

    def run(self, VERSION):
        self.version = VERSION
        self.setup()
        self.TOKEN = os.getenv('TOKEN')

        print("Running...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Bot Connected")
        while True:
            if datetime.datetime.now().minute % 5 == 0:
                game = choice(status_list)
                await self.change_presence(activity=discord.Game(game))
            await sleep(60)

    async def on_disconnect(self):
        print("Bot Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong")

        # channel= self.get_channel(channel_id)
        # await channel.send("Ocorreu um erro")

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            await ctx.send("Comando inválido")

        elif hasattr(exc, "original"):
            raise exc.original
        else:
            raise exc

    async def on_ready(self, ctx):
        if not self.ready:
            # self.guild=self.get_guild(guild_id)

            ''' EMBED DE INFO - Está a funcionar como comando em fun.py > command "info"
            channel = self.get_channel(channel_id)

            embed= Embed(title="**DJ PaixHug - Music Bot**", description="",
                         colour=0x248BFF, timestamp=datetime.utcnow())
            fields = [("`Type`","Music Bot",True),
                      ("`Prefix`","%", True),
                      ("`Playing`","Playlist do Hugo", False)]
            for name,value,inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_author(name="Gaming Nerds Bot - Padjojé & Hugo", icon_url=os.getenv('DAISY_IMG'))
            embed.set_footer(text="Bot em construção")
            embed.set_thumbnail(url=os.getenv('TROLL_IMG'))
            await channel.send(embed=embed)
            '''

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True

        else:
            print("Bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
