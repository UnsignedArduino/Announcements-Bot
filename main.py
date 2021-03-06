# OAuth2 URL: https://discord.com/api/oauth2/authorize?client_id=819982964297039872&permissions=26624&scope=bot
# Scopes: bot
# Bot perms: Send Messages, Embed Links, Manage Messages

import os
import discord
from discord.ext import commands, tasks
from pretty_help import PrettyHelp
from dotenv import load_dotenv
import json
from pathlib import Path
from time import time as unix
import arrow
import logging
from create_logger import create_logger

CONFIG_PATH = Path.cwd() / "config.json"

logger = create_logger(name=__name__, level=logging.DEBUG)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="~", help_command=PrettyHelp(show_index=False, no_category="Commands",
                                                               color=discord.Color(0xff7069)))

config = json.loads(CONFIG_PATH.read_text())
logger.debug(f"Configuration:\n{repr(config)}")


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to {len(bot.guilds)} guild(s)!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="~help"))
    check_to_send.start()


@bot.command(name="ping", help="Gets the latency of the bot")
async def ping(ctx):
    logger.debug(f"Ping requested from {repr(ctx)}")
    ping_ms = round(bot.latency * 1000)
    logger.debug(f"Ping is {repr(ping_ms)} ms")
    embed = discord.Embed(title="🏓 Pong! 🏓", description=f"Latency is {ping_ms} ms!", color=0xff7069)
    await ctx.send(embed=embed)


@bot.command(name="list", help="Lists all announcements")
async def list_announcements(ctx):
    logger.debug(f"List of announcements requested from {repr(ctx)}")
    embed = discord.Embed(title="📃 Announcements list 📃",
                          description="List of announcements - use ~status announcement_name to check its status!",
                          color=0xff7069)
    if len(config["announcements"]) > 0:
        for announcement in config["announcements"]:
            logger.debug(f"Adding announcement {repr(announcement['name'])} to embed!")
            embed.add_field(name=announcement["pretty_name"],
                            value=f"{announcement['name']} - {'active' if announcement['enabled'] else 'disabled'}",
                            inline=True)
    else:
        embed.add_field(name="No announcement found!",
                        value="Please edit the configuration file for more announcements!", inline=True)
    await ctx.send(embed=embed)


@bot.command(name="status", help="Gets the status of an announcement")
async def announcement_status(ctx, name: str):
    logger.debug(f"Status of announcement requested from {repr(ctx)}")
    specified_announcement = None
    for announcement in config["announcements"]:
        if announcement["name"] == name:
            specified_announcement = announcement
    embed = discord.Embed(title="📢 Announcement 📢", description=f"Status of announcement {repr(name)}", color=0xff7069)
    if specified_announcement is None:
        embed.add_field(name="Error!",
                        value="That is not an announcement! You can list announcements with the ~list command!",
                        inline=True)
    else:
        embed.add_field(name="Pretty name", value=specified_announcement["pretty_name"], inline=True)
        embed.add_field(name="Enabled", value=specified_announcement["enabled"], inline=True)
        embed.add_field(name="Last triggered", value=arrow.get(specified_announcement["last_sent"]).humanize(),
                        inline=True)
        embed.add_field(name="Delay",
                        value=arrow.get(unix() - specified_announcement["delay"]).humanize(only_distance=True),
                        inline=True)
    await ctx.send(embed=embed)


@bot.command(name="enable", help="Enables an announcement")
async def enable(ctx, name: str):
    logger.debug(f"Enabling announcement requested from {repr(ctx)}")
    specified_announcement = None
    for announcement in config["announcements"]:
        if announcement["name"] == name:
            specified_announcement = announcement
    embed = discord.Embed(title="📢 Announcement 📢", description=f"Enable announcement {repr(name)}", color=0xff7069)
    if specified_announcement is None:
        embed.add_field(name="Error!",
                        value="That is not an announcement! You can list announcements with the ~list command!",
                        inline=True)
    else:
        specified_announcement["enabled"] = True
        logger.debug(f"Saving configuration to {repr(CONFIG_PATH)}...")
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
        embed.add_field(name="✅ Success! ✅", value=f"Announcement {repr(name)} successfully enabled!", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="disable", help="Disables an announcement")
async def disable(ctx, name: str):
    logger.debug(f"Disabling announcement requested from {repr(ctx)}")
    specified_announcement = None
    for announcement in config["announcements"]:
        if announcement["name"] == name:
            specified_announcement = announcement
    embed = discord.Embed(title="📢 Announcement 📢", description=f"Disable announcement {repr(name)}", color=0xff7069)
    if specified_announcement is None:
        embed.add_field(name="Error!",
                        value="That is not an announcement! You can list announcements with the ~list command!",
                        inline=True)
    else:
        specified_announcement["enabled"] = False
        logger.debug(f"Saving configuration to {repr(CONFIG_PATH)}...")
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
        embed.add_field(name="✅ Success! ✅", value=f"Announcement {repr(name)} successfully disabled!", inline=False)
    await ctx.send(embed=embed)


@tasks.loop(minutes=1)
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


# TODO: Override the ugly built in help


@bot.event
async def on_command_error(ctx, error):
    logger.exception("Uh oh! An exception has occurred!")
    embed = discord.Embed(title="⚠️ Error! ⚠️", description="😕 An error has occurred!", color=0xff7069)
    embed.add_field(name="Error:", value=error, inline=True)
    await ctx.send(embed=embed)


bot.run(TOKEN)
