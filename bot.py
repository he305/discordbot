from discord.ext.commands import Bot
from animelist import get_data
from forecast import weather
import os
from music import Music
from anime_feed import Feeder
from rkn import BlockInfo

BOT_PREFIX = ('?', '!')
TOKEN = os.environ.get('TOKEN')

client = Bot(command_prefix=BOT_PREFIX)
client.add_cog(Music(client))
client.add_cog(BlockInfo(client))
feeder = Feeder(client)
client.loop.create_task(feeder.feed('he3050'))


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
    pass


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
