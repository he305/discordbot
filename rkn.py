import requests
import asyncio
from discord.ext import commands
import datetime
import pytz


class BlockInfo:
    def __init__(self, client):
        self.client = client
        self.url = "https://usher2.club/d1_ipblock.json"
        self.last_ip = 0

    @commands.command(name="rkn", pass_context=True)
    async def rkn(self, ctx, minimum):
        await self.client.send_message(ctx.message.channel, "Начат сбор данных с https://usher2.club/")
        self.client.loop.create_task(self.run(ctx.message.channel, int(minimum)))

    async def run(self, channel, minimum):
        while True:
            try:
                data = requests.get(self.url).json()
            except TimeoutError as t:
                print(t)
                continue

            if self.last_ip != data[-1]['y']:
                sub = data[-1]['y'] - self.last_ip
                if sub >= minimum:
                    d = datetime.datetime.utcnow()
                    d = d.replace(tzinfo=datetime.timezone.utc).astimezone(tz=pytz.timezone("Europe/Moscow"))
                    time = d.strftime("%Y-%m-%d %H-%M-%S")

                    message = "@everyone\nОбновление от {}\n".format(time)
                    if sub < 0:
                        message += "-{} айпи".format(sub)
                    else:
                        message += "+{} айпи".format(sub)
                    await self.client.send_message(channel, message)

                    self.last_ip = data[-1]['y']

            await asyncio.sleep(300)
