import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
import json
from pathlib import Path
from time import time as unix
import logging
from create_logger import create_logger

CONFIG_PATH = Path.cwd() / "config.json"

logger = create_logger(name=__name__, level=logging.DEBUG)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="~")

config = json.loads(CONFIG_PATH.read_text())
logger.debug(f"Configuration:\n{repr(config)}")


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to {len(bot.guilds)} guild(s)!")
    check_to_send.start()


@tasks.loop(minutes=0, seconds=2)
async def check_to_send():
    logger.debug(f"Checking for messages to send...")
    for announcement in config["announcements"]:
        logger.debug(f"Checking for message {repr(announcement['name'])}...")
        next_send = announcement["last_sent"] + announcement["delay"]
        if next_send < unix():
            logger.debug(f"{repr(announcement['name'])} is due by {repr(next_send - unix())} seconds!")
            announcement["last_sent"] = unix()
    logger.debug(f"Saving configuration to {repr(CONFIG_PATH)}...")
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    logger.debug(f"Finished!")


bot.run(TOKEN)
