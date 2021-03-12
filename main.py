import os
from discord.ext import commands
from dotenv import load_dotenv
import logging
from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="~")


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to {len(bot.guilds)} guild(s)!")


bot.run(TOKEN)
