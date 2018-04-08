from discord.ext.commands import Bot
from getlist import get_data
from forecast import weather
import os


BOT_PREFIX = ('?', '!')
TOKEN = os.environ.get('TOKEN')

client = Bot(command_prefix=BOT_PREFIX)

@client.command(name="anime",
                description="Get anime list for specific user",
                pass_context=True)
async def get_anime(ctx, nickname='he3050'):
    await client.say("Starting collecting data for {}".format(ctx.message.author.mention))
    animes = get_data(nickname)

    data = ""
    for anime in animes:
        data += anime.form_full_info() + '\n'

    await client.say(data)
    await client.say("Complete {}".format(ctx.message.author.mention))


@client.command(name="weather")
async def get_weather():
    data = weather()
    await client.say(data)

@client.event
async def on_ready():
    pass

client.run(TOKEN)