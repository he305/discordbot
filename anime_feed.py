from discord.ext import commands
from animelist import get_data
import feedparser
import asyncio
import requests
import re


class Feeder:
    def __init__(self, client):
        self.rss_feed = []
        self.client = client
        self.running = False

    @commands.command(pass_context=True)
    async def feed(self, ctx, nickname):
        data = get_data(nickname)
        if len(data) == 0:
            await self.client.say("No data available")
            return
        await self.client.say("Starting reading rss for {}".format(nickname))
        self.running = True
        self.client.loop.create_task(self.feed_loop(ctx, nickname))
        #self.client.loop.create_task(self.clear_feed())

    @commands.command(pass_context=True)
    async def stop_feed(self, ctx):
        if self.running:
            self.running = False
            self.rss_feed.clear()
            await self.client.send_message(ctx.message.channel, "Feeding rss stopped")

    async def feed_loop(self, ctx, nickname):
        await self.client.wait_until_ready()
        while self.running:
            skipped = [self.remove_characters(c.name)
                       for c in get_data(nickname) if c.is_skipped()]

            if len(skipped) != 0:
                rss = feedparser.parse("http://horriblesubs.info/rss.php?res=1080")

                for entry in rss.entries:
                    title = self.fix_rss_title(entry.title)
                    if title in skipped and title not in self.rss_feed:
                        link = requests.get("http://mgnet.me/api/create?m=" + entry.link).json()
                        data = "{}\nNew series: {}\n[Link]({})".format(ctx.message.author.mention, entry.title, link['shorturl'])
                        await self.client.send_message(ctx.message.channel, data)
                        self.rss_feed.append(title)
                print("Rss has been read")
            await asyncio.sleep(600)

    # async def clear_feed(self):
    #     await self.client.wait_until_ready()
    #     while self.running:
    #         await asyncio.sleep(86400)
    #         self.rss_feed.clear()

    def remove_characters(self, st):
        st = st.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).lower()
        return " ".join(st.split())


    def fix_rss_title(self, st):
        new_str = st.replace('[HorribleSubs] ', '')
        pattern = r'(^[a-zA-Z0-9\s!\'@#$%^&*()\[\]\{\}\;\:\,\.\/\<\>\?\|\`\~\-\=\_\+]*) - \d+'
        return self.remove_characters(re.match(pattern, new_str).group(1)) #st.split(' -')[0])