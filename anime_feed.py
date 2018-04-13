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
        self.anime_data_cached = []

    @commands.command(pass_context=True)
    async def feed(self, ctx, nickname):
        self.anime_data_cached = get_data(nickname)
        if len(self.anime_data_cached) == 0:
            await self.client.say("No data available")
            return

        await self.client.say("Overwatched animes:")
        for anime in self.anime_data_cached:
            await self.client.say(anime.name)

        await self.client.say("Starting reading rss for {}".format(nickname))
        self.running = True
        self.client.loop.create_task(self.feed_loop(ctx, nickname))
        # self.client.loop.create_task(self.clear_feed())

    @commands.command(pass_context=True)
    async def stop_feed(self, ctx):
        if self.running:
            self.running = False
            self.rss_feed.clear()
            await self.client.send_message(ctx.message.channel, "Feeding rss stopped")

    async def feed_loop(self, ctx, nickname):
        await self.client.wait_until_ready()
        while self.running:
            anime_data_full = get_data(nickname)
            anime_data = [self.remove_characters(c.get_all_names())
                          for c in anime_data_full]

            if len(anime_data) != 0:
                if len(anime_data_full) != len(self.anime_data_cached):
                    print(anime_data_full)
                    print(self.anime_data_cached)
                    new_data = [item.name for item in anime_data_full if item.name not in
                                [c.name for c in self.anime_data_cached]]
                    if len(new_data) != 0:
                        await self.client.send_message(ctx.message.channel, "New animes are found:")
                        for item in new_data:
                            await self.client.send_message(ctx.message.channel, item)

                    self.anime_data_cached = anime_data_full

                rss = feedparser.parse("http://horriblesubs.info/rss.php?res=1080")

                for entry in rss.entries:
                    title = self.fix_rss_title(entry.title)
                    if len([s for s in anime_data if title in s]) != 0 and entry not in self.rss_feed:
                        link = requests.get("http://mgnet.me/api/create?m=" + entry.link).json()
                        data = "{}\nNew series: {}\n[Link]({})".format(ctx.message.author.mention, entry.title,
                                                                       link['shorturl'])
                        await self.client.send_message(ctx.message.channel, data)
                        self.rss_feed.append(entry)
                print("Rss has been read")
            await asyncio.sleep(600)

    # async def clear_feed(self):
    #     await self.client.wait_until_ready()
    #     while self.running:
    #         await asyncio.sleep(86400)
    #         self.rss_feed.clear()

    def remove_characters(self, st):
        st = st.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).lower()

        # delete_season_pattern
        st = re.sub('s\d+', '', st)
        return " ".join(st.split())

    def fix_rss_title(self, st):
        new_str = st.replace('[HorribleSubs] ', '')
        pattern = r'(^[a-zA-Z0-9\s!\'@#$%^&*()\[\]\{\}\;\:\,\.\/\<\>\?\|\`\~\-\=\_\+]*) - \d+'
        return self.remove_characters(re.match(pattern, new_str).group(1))  # st.split(' -')[0])
