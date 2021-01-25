from discord.ext import commands
from anime_list import AnimeListProvider
import feedparser
import asyncio
import aiohttp
import re
from proxy import Proxy
from torrent import Torrent
from hidden_data import PROXY_REQUIRED

import logging
log = logging.getLogger(__name__)


class Feeder:
    def __init__(self, client):
        """
        :param client: Discord.Client
        """
        self.proxy = Proxy()
        self.torrent = Torrent()
        self.rss_feed = []
        self.client = client
        self.running = False
        self.anime_data_cached = []
        self.channel = ""

        # Have to use it because sometimes mal/shikimori titles completely mismatch from nyaa.si titles
        # Current regex algorithm cannot solve this problem
        self.special_cases = []

        self.anime_provider = AnimeListProvider()

    async def feed(self, nickname):
        """
        Starting feeding horriblesubs rss for new anime for watching
        list provided by nickname
        :param ctx: Discord.Context
        :param nickname: nickname at myanimelist
        :return:
        """
        await self.client.wait_until_ready()
        for server in self.client.guilds:
            for channel in server.channels:
                if channel.name == "anime-feed":
                    self.channel = channel
                    break

        self.anime_data_cached = await self.anime_provider.get_anime_list(nickname)
        while not self.anime_data_cached:
            await asyncio.sleep(30)
            await self.channel.send("Anime list is down, trying to reconnect...")
            self.anime_data_cached = await self.anime_provider.get_anime_list(nickname)

        for anime in self.anime_data_cached:
            if anime.watching_status == 1 or anime.watching_status == 6:
                await anime.get_synonyms()
                await asyncio.sleep(3)

        await self.proxy.get_new()
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
            await self.channel.send("Admin permission required for this command")
            return
        if self.running:
            self.running = False
            self.rss_feed.clear()
            await self.channel.send("Feeding rss stopped")

    async def feed_loop(self, nickname):
        """
        Getting fresh anime data using provided nickname for checking
        horriblesubs rss for getting info about new series
        :param nickname: nickname at myanimelist
        :return:
        """
        await self.client.wait_until_ready()
        async with aiohttp.ClientSession() as session:
            while self.running:
                anime_data_full = await self.anime_provider.get_anime_list(nickname)
                while not anime_data_full:
                    await asyncio.sleep(30)
                    anime_data_full = await self.anime_provider.get_anime_list(nickname)

                new_data = []
                for item in anime_data_full:
                    found = False
                    for item_cached in self.anime_data_cached:
                        if item.name == item_cached.name:
                            found = True
                            if item == item_cached:
                                break
                            else:
                                new_data.append(item)
                                break
                    if not found:
                        new_data.append(item)

                if new_data:
                    await self.channel.send("New animes are found:")
                    for item in new_data:
                        if item.watching_status == 1:
                            await self.channel.send("New watching: {}".format(item.name))
                        if item.watching_status == 2:
                            await self.channel.send("New completed: {} Score: {}".format(item.name, item.score))
                        if item.watching_status == 3:
                            await self.channel.send("New onhold: {}".format(item.name))
                        if item.watching_status == 4:
                            await self.channel.send("New dropped: {} Score: {}".format(item.name, item.score))
                        if item.watching_status == 6:
                            await self.channel.send("New planned to watch: {}".format(item.name))

                    self.anime_data_cached = anime_data_full
                    for anime in self.anime_data_cached:
                        if anime.watching_status == 1 or anime.watching_status == 6:
                            await anime.get_synonyms()
                            await asyncio.sleep(3)

                anime_data = [self.remove_characters(c.get_all_names())
                            for c in self.anime_data_cached if c.watching_status == 1 or c.watching_status == 6]
                    
                anime_data += self.special_cases  # See init
                # log.info("Anime data: {}".format(anime_data))
                print(anime_data)

                rss = []
                i = 0
                while not rss:
                    try:
                        proxy = self.proxy.current if PROXY_REQUIRED else None
                        async with session.get('https://nyaa.si/?page=rss', timeout=5, proxy=proxy) as resp:
                            rss = feedparser.parse(await resp.text())
                    except IndexError:
                            rss = []
                    except Exception as e:
                        if i > 5:
                            await self.proxy.get_new()
                            i = 0
                        print("Failed to load Nyaa.si: {}".format(repr(e)))
                        log.warning("Failed to load Nyaa.si: {}".format(repr(e)))
                        self.proxy.changeCurrent()
                        i += 1
                        await asyncio.sleep(5)

                i = 0

                # RIP HorribleSubs
                # pattern = '[HorribleSubs] '
                # headers = {'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'}
                # while i <= 5:
                #     try:
                #         async with session.get("https://horriblesubs.info", timeout=10, headers=headers) as resp:
                #             if resp.status == 502:
                #                 pattern = '[Erai-raws] '  # if HorribleSubs is offline
                #             elif resp.status == 200:
                #                 break
                #     except Exception as e:
                #         print("Error connecting to HorribleSubs: {}".format(repr(e)))
                #         log.warning("Error connecting to HorribleSubs: {}".format(repr(e)))
                #         i += 1
                #         if i > 5:
                #             print("Serious connection errors with HorribleSubs, changing pattern to Erai-raws")
                #             log.warning("Serious connection errors with HorribleSubs, changing pattern to Erai-raws")
                #             pattern = '[Erai-raws] '
                #         await asyncio.sleep(5)

                pattern = '[Erai-raws] '

                for entry in rss.entries:
                    if pattern not in entry.title or '1080p' not in entry.title:
                        continue

                    title = entry.title.replace(pattern, '')
                    title = self.fix_rss_title(title)
                    if [s for s in anime_data if title in s] and entry.title not in self.rss_feed:
                        data = "{}\nNew series: {}\n[Link]({})".format('@everyone', entry.title, entry.link)
                        await self.channel.send(data)
                        if await self.torrent.add_torrent(entry.link):
                            await self.channel.send("Successfully added torrent: {}".format(entry.link))

                        self.rss_feed.append(entry.title)
                log.info("Rss has been read")
                print("Rss has been read")
                await asyncio.sleep(300)

    def remove_characters(self, st):
        """
        Replace all special characters for spaces
        :param st: string to be replaced
        :return:
        """
        st = st.translate({ord(c): " " for c in "'!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).lower()

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
