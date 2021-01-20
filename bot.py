from hidden_data import TOKEN
import discord

from discord.ext.commands import Bot
from anime_list import get_data
from forecast import weather
from anime_feeder import Feeder
from rkn import BlockInfo
import asyncio
from datetime import datetime
import pytz
from vk_api import send_message

from streamer_feeder import StreamerFeeder
from motion import Motion

from search_image import SearchImage

import logging
logging.basicConfig(filename='logging.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

BOT_PREFIX = ('?', '!')

client = Bot(command_prefix=BOT_PREFIX)

streamer_feeder = StreamerFeeder(client)
client.loop.create_task(streamer_feeder.feed())

# client.add_cog(BlockInfo(client))
anime_feeder = Feeder(client)
client.loop.create_task(anime_feeder.feed('he3050'))

# motion_feeder = Motion(client)
# client.loop.create_task(motion_feeder.feed())

client.add_cog(SearchImage(client))

@client.command(name="anime",
                description="Get anime list for specific user")
async def get_anime(ctx, nickname='he3050'):
    """
    Get anime list from mal by nickname
    :param ctx: Discord.Context
    :param nickname: nickname at myanimelist
    :return:
    """
    await ctx.channel.send("Starting collecting data for {}".format(ctx.message.author.mention))
    animes = await get_data(nickname)
    for anime in animes:
        if anime.watching_status == 1:
            await ctx.channel.send(anime.form_full_info() + '\n')

    await ctx.channel.send("Complete {}".format(ctx.message.author.mention))


@client.command(name="weather")
async def get_weather(ctx):
    """
    Get current weather in Elektrostal, RU
    :return:
    """
    data = weather()
    await ctx.channel.send(data)


@client.event
async def on_ready():
    print("Bot has been restarted")
    # for server in client.servers:
    #     for channel in server.channels:
    #         if channel.name == "bot-debug":
    #             await client.send_message(channel, "Bot has been restarted")

    #             headers = {
    #                 "Accept": "application/vnd.github.v3+json"
    #             }

    #             data = requests.get("https://api.github.com/repos/he305/discordbot/commits", headers=headers).json()
    #             await client.send_message(channel, "Last commit: {}".format(data[0]['commit']['message']))
    #             break


@client.command(name="сидим")
async def sit(ctx):
    """
    Send picture for describing main philosophy of life
    :param ctx: Discord.Context
    :return:
    """
    await ctx.channel.send(file=discord.File('pics/sidim.jpg'))


@client.command(pass_context=True)
async def clear(ctx):
    """
    Clears 100 channel messages
    :param ctx: Discord.Context
    :return:
    """
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("Admin permission required for this command")
        return
    msg = []
    print(ctx.message.channel)
    async for x in ctx.channel.history():
        msg.append(x)
    await ctx.channel.delete_messages(msg)


client.run(TOKEN)
