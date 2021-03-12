import os
from discord.ext import commands, tasks
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
    check_to_send.start()


@tasks.loop(minutes=1)
async def check_to_send():
    logger.debug(f"Checking for messages to send...")
    logger.debug(f"Finished!")


bot.run(TOKEN)
