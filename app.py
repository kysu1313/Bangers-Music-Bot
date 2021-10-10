
from discord.ext.commands import Bot
from helpers.settings import Settings
import discord
import os
import platform

coins = ['AUR','BCH','BTC','DASH','DOGE','EOS','ETC','ETH','GRC','LTC','MZC','NANO','NEO','NMC','NXT','POT','PPC','TIT','USDC','USDT','VTC','XEM','XLM','XMR','XPM','XRP','XVG','ZEC']
greetings = ['hiya', 'hi', 'hey', 'yo', 'hello', 'whats up', "what's up", 'yoo', 'yooo', 'sup', 'ayo', 'ayoo', 'howdy']
times = {}
description = '''None of your business, mkay'''
BOT_ID = ""
ENABLED = True
settings = None
STARTING_MONEY = 500
LAST_EVENTS = {}
STOP_SPAM = {}
SLOW_MODE = False
MESSAGE_INTERVAL = 0


#################################################
####### IMPORTANT: CHANGE FOR PRODUCTION ########
#################################################
PROD_MODE = False
DOCKER = True


intents = discord.Intents.all()
client = discord.Client()
bot = Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")

@bot.event
async def on_command_completion(ctx):
    '''
        Print commands as they are executed.

        Attributes:
            ctx: user who sent command
        '''
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    print(
        f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.event
async def on_message(message):
    '''
        General message listener.
        Attributes:
            message: the message to check
    '''
    global ENABLED, LAST_EVENTS, SLOW_MODE, MESSAGE_INTERVAL, STOP_SPAM
    if '!startbot' in message.content:
        await message.channel.send("I'm alive! 😃")
        ENABLED = True
    if ENABLED:

        if message.author == bot.user:
            return

        if message.author.name == "Lil-Bot" or message.author.name == "Test-Bot":
            return

        msg = message.content.lower()

        if '!stopbot' in msg:
            ENABLED = False
            await message.channel.send("ok, I'll be quiet 😔")
            return

        await bot.process_commands(message)

# Activate all commands in cog classes
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# Run the bot
if __name__ == '__main__':
    ENABLED = True
    settings = Settings(PROD_MODE, DOCKER)
    TOKEN = settings.get_bot_token()
    print("Setting tokens")
    bot.run(TOKEN)
    print("Tokens set successfully")

