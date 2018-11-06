from discord.ext import commands
from anime_list import get_data
from vk_api import send_message
import feedparser
import asyncio
import requests
import re


class Feeder:
    def __init__(self, client):
        """

        :param client: Discord.Client
        """
        self.rss_feed = []
        self.client = client
        self.running = False
        self.anime_data_cached = []
        self.channel = ""

        #Have to use it because sometimes mal/shikimori titles completely mismatch from nyaa.si titles
        #Current regex algorithm cannot solve this problem
        self.special_cases = ["jojo's bizarre adventure golden wind"]

    async def feed(self, nickname):
        """
        Starting feeding horriblesubs rss for new anime for watching
        list provided by nickname
        :param ctx: Discord.Context
        :param nickname: nickname at myanimelist
        :return:
        """
        await self.client.wait_until_ready()

        for server in self.client.servers:
            for channel in server.channels:
                if channel.name == "anime-feed":
                    self.channel = channel
                    break

        self.anime_data_cached = get_data(nickname)
        while not self.anime_data_cached:
            await asyncio.sleep(600)
            await self.client.send_message(self.channel, "Anime list is down, trying to reconnect...")
            self.anime_data_cached = get_data(nickname)

        self.running = True
        self.client.loop.create_task(self.feed_loop(nickname))
        # self.client.loop.create_task(self.clear_feed())

    @commands.command(pass_context=True)
    async def stop_feed(self, ctx):
        """
        Stop feeding rss if process has been started
        :param ctx: Discord.Context
        :return:
        """
        if not ctx.message.author.server_permissions.administrator:
            await self.client.send_message(ctx.message.channel, "Admin permission required for this command")
            return
        if self.running:
            self.running = False
            self.rss_feed.clear()
            await self.client.send_message(ctx.message.channel, "Feeding rss stopped")

    async def feed_loop(self, nickname):
        """
        Getting fresh anime data using provided nickname for checking
        horriblesubs rss for getting info about new series
        :param nickname: nickname at myanimelist
        :return:
        """
        await self.client.wait_until_ready()
        while self.running:
            anime_data_full = get_data(nickname)
            while not anime_data_full:
                await asyncio.sleep(600)
                await self.client.send_message(self.channel, "Anime list is down, trying to reconnect...")
                anime_data_full = get_data(nickname)

            anime_data = [self.remove_characters(c.get_all_names())
                          for c in anime_data_full]
            anime_data += self.special_cases #See init
            

            if len(anime_data) != 0:
                if len(anime_data_full) != len(self.anime_data_cached):
                    print(anime_data_full)
                    print(self.anime_data_cached)
                    new_data = [item.name for item in anime_data_full if item.name not in
                                [c.name for c in self.anime_data_cached]]
                    if len(new_data) != 0:
                        await self.client.send_message(self.channel, "New animes are found:")
                        for item in new_data:
                            await self.client.send_message(self.channel, item)

                    self.anime_data_cached = anime_data_full

                try:
                    r = requests.get('https://nyaa.si/?page=rss', timeout=10)
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    await self.client.send_message(self.channel, "Nyaa.si is down")
                    await asyncio.sleep(600)
                    continue
                else:
                    rss = feedparser.parse(r.text)

                pattern = '[HorribleSubs] '
                if requests.get("http://horriblesubs.info/rss.php?res=1080.xml").status_code == 502:
                    pattern = '[Erai-raws] '  # if HorribleSubs is offline

                for entry in rss.entries:
                    if pattern not in entry.title or '1080p' not in entry.title:
                        continue

                    title = entry.title.replace(pattern, '')
                    title = self.fix_rss_title(title)
                    if len([s for s in anime_data if title in s]) != 0 and entry.title not in self.rss_feed:
                        data = "{}\nNew series: {}\n[Link]({})".format('@everyone', entry.title, entry.link)
                        await self.client.send_message(self.channel, data)
                        #send_message(data)
                        self.rss_feed.append(entry.title)
                print("Rss has been read")
            await asyncio.sleep(300)

    def remove_characters(self, st):
        """
        Replace all special characters for spaces
        :param st: string to be replaced
        :return:
        """
        st = st.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).lower()

        # delete_season_pattern
        st = re.sub('s\d+', '', st)
        return " ".join(st.split())

    def fix_rss_title(self, st):
        """
        Fix horriblesubs title for comprasion with mal titles
        Example: Steins;Gate 0 - 01 [1080p].mkv -> steins gate 0
        :param st: string to be fixed
        :return:
        """
        pattern = r'(^[a-zA-Z0-9\s!\'@#$%^&*()\[\]\{\}\;\:\,\.\/\<\>\?\|\`\~\-\–\=\_\+]*) [-–] \d+'
        try:
            title = self.remove_characters(re.match(pattern, st).group(1))
            return title
        except AttributeError:
            print("Attribute error: " + st)
            return st
