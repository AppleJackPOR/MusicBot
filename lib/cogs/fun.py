import os
from dotenv import load_dotenv


from discord.ext.commands import Cog
from discord.ext.commands import command
from datetime import datetime
from discord import Embed
from discord.ext.commands import Bot as BotBase 

load_dotenv()

class Fun(Cog, BotBase):
    def __init__(self,bot):
        self.bot=bot
        self.guild = None


    @command(name="info", aliases=["inf"])
    async def show_info(self,ctx):
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
        await ctx.send(embed=embed)


    @command(name="ping")
    async def send_ping(self, ctx):
        await ctx.send("pong")


    @command(name="join")
    async def send(self,ctx):
        channel = ctx.message.author.voice.channel
        print(channel)
        await channel.connect()

    '''
    @command(name="leave", aliases=["disconnect", "baza"])
    async def leave_voice(self, ctx):
        await ctx.voice_client.disconnect()
    '''


    @command(name="hello", aliases=["hi", "Hi", "Hello"])
    async def say_hello(self, ctx):
        #apaga a mensagem do user
        #await ctx.message.delete()
        
        await ctx.send(f"Olá {ctx.author.mention}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")
    
def setup(bot):
    bot.add_cog(Fun(bot))