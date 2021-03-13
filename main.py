import os
import discord
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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="~"))
    check_to_send.start()


@tasks.loop(minutes=0, seconds=2)
async def check_to_send():
    logger.debug(f"Checking for messages to send...")
    for announcement in config["announcements"]:
        logger.debug(f"Checking for message {repr(announcement['name'])}...")
        next_send = announcement["last_sent"] + announcement["delay"]
        if next_send < unix():
            logger.debug(f"{repr(announcement['name'])} is due by {repr(unix() - next_send)} seconds!")
            announcement["last_sent"] = unix()
            if announcement["enabled"]:
                channel = bot.get_channel(announcement["id"])
                logger.debug(f"Getting channel {repr(channel)} (ID: {repr(announcement['id'])})")
                logger.debug(f"Sending message with a length of {repr(len(announcement['message']))} characters")
                await channel.send(announcement["message"])
            else:
                logger.debug(f"Would have sent message, but this announcement is disabled!")
    logger.debug(f"Saving configuration to {repr(CONFIG_PATH)}...")
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    logger.debug(f"Finished!")


bot.run(TOKEN)
