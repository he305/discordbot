from discord.ext.commands import Bot
from anime_list import get_data
from forecast import weather
import os
#from music import Music
from anime_feeder import Feeder
from rkn import BlockInfo
import requests
import asyncio
from datetime import datetime
import pytz
from vk_api import send_message

from streamer_feeder import StreamerFeeder

BOT_PREFIX = ('?', '!')
TOKEN = os.environ.get('TOKEN')

client = Bot(command_prefix=BOT_PREFIX)
#client.add_cog(Music(client))
client.add_cog(BlockInfo(client))
anime_feeder = Feeder(client)
client.loop.create_task(anime_feeder.feed('he3050'))

streamer_feeder = StreamerFeeder(client)
client.loop.create_task(streamer_feeder.feed())

async def todo():
    tz = pytz.timezone("Europe/Moscow")
    todolist = "1. Еда\n2. Зонт\n3. Флешка"
    while True:
        current_time = datetime.now(tz)
        if (current_time.hour == 7 and current_time.minute <= 15 and current_time.weekday() <= 4):
            send_message(todolist)
        await asyncio.sleep(900)

client.loop.create_task(todo())


@client.command(name="anime",
                description="Get anime list for specific user",
                pass_context=True)
async def get_anime(ctx, nickname='he3050'):
    """
    Get anime list from mal by nickname
    :param ctx: Discord.Context
    :param nickname: nickname at myanimelist
    :return:
    """
    await client.say("Starting collecting data for {}".format(ctx.message.author.mention))
    animes = get_data(nickname)

    data = ""
    for anime in animes:
        data += anime.form_full_info() + '\n'

    await client.say(data)
    await client.say("Complete {}".format(ctx.message.author.mention))


@client.command(name="weather")
async def get_weather():
    """
    Get current weather in Elektrostal, RU
    :return:
    """
    data = weather()
    await client.say(data)


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


@client.command(name="сидим",
                pass_context=True)
async def sit(ctx):
    """
    Send picture for describing main philosophy of life
    :param ctx: Discord.Context
    :return:
    """
    await client.send_file(ctx.message.channel, 'pics/sidim.jpg')


@client.command(pass_context=True)
async def clear(ctx):
    """
    Clears 100 channel messages
    :param ctx: Discord.Context
    :return:
    """
    if not ctx.message.author.server_permissions.administrator:
        await client.say("Admin permission required for this command")
        return
    msg = []
    print(ctx.message.channel)
    async for x in client.logs_from(ctx.message.channel):
        msg.append(x)
    await client.delete_messages(msg)


client.run(TOKEN)
