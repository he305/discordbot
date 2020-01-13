import asyncio
import json
import aiohttp
import logging

from vk_api import get_new_posts
from streamer_utills import get_channel_by_name
from streamer_info import StreamerInfoTwitch

from hidden_data import CLIENT_ID
MIN_LIKES = 10

log = logging.getLogger(__name__)


class StreamerFeeder:
    def __init__(self, client):
        self.client = client
        self.streamers = []
        #self.streamer_live = []
        #self.goodgame = []
        #self.goodgames_live = []
        self.groups = {}

        self.group_posts = []
        self.comments = []
        self.running = False
        self.channel = None

        self.headers = {
            'Client-ID': CLIENT_ID,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }

    async def feed(self):
        await self.client.wait_until_ready()

        with open("streamers.json", 'r', encoding='utf8') as f:
            streamers = json.load(f)

        for streamer in streamers["twitch"]:
            name = streamer["name"]
            if streamer["id"] is None:
                id = await get_channel_by_name(streamer["name"])
            else:
                id = streamer["id"]

            self.streamers.append(StreamerInfoTwitch(name, id))

        for streamer in self.streamers:
            log.info(streamer)

        with open('groups.json', 'r', encoding="utf8") as f:
            self.groups = json.load(f)

        for server in self.client.guilds:
            for channel in server.channels:
                if channel.name == "streamer-feed":
                    self.channel = channel
                    break

        self.running = True
        self.client.loop.create_task(self.feed_loop())
        self.client.loop.create_task(self.group_feed_loop())

    async def group_feed_loop(self):
        while self.running:
            for group in self.groups:
                res = await get_new_posts(int(group))

                if len(self.group_posts) > 1:
                    print(self.group_posts[0])
                    print(self.group_posts[1])

                url = ""
                if 'attachments' in res:
                    for att in res['attachments']:
                        if att['type'] == 'photo':
                            url = att['photo']['text'].replace('Original: ', '')
                text = ""
                if 'text' in res:
                    text = res['text']
                data = "@everyone\n{}{}{}".format(self.groups[group], '\n' + text, '\n' + url)

                current_time = time.time()

                offset = current_time - int(res['date'])
                if data not in self.group_posts and offset < 600 * len(self.groups):
                    self.group_posts.append(data)
                    await self.channel.send(data)
    
                # comments = get_post_comments(group, res['id'])
    
                # for comment in comments:
                #     if int(comment['likes']['count']) > MIN_LIKES:
                #         url = ""
                #         if 'attachments' in comment:
                #             for att in comment['attachments']:
                #                 if att['type'] == 'photo':
                #                     for size in att['photo']['sizes']:
                #                         if size['type'] == "x":
                #                             url = size['url']
                #                             break
                #         text = ""
                #         if 'text' in comment:
                #             text = comment['text']
    
                #         data = "\n{}{}\nURL: {}".format(text, '\n' + url, "https://vk.com/{}?w=wall-{}_{}_r{}".format(self.groups[group], group, res['id'], comment['id']))
    
                #         if data not in self.comments:
                #             self.comments.append(data)
                #             await self.channel.send(data)
    
                await asyncio.sleep(300)

    async def feed_loop(self):
        while self.running:
            for streamer in self.streamers:
                status = await streamer.get_status()

                if status and not streamer.status:
                    streamer.status = True
                    data = await streamer.init_at_start()
                    await self.channel.send(data)
                elif not status and streamer.status:
                    streamer.status = False
                    await self.channel.send(f"{streamer.name} went offline")

                await asyncio.sleep(1)

                if not status:
                    continue
                processData = await streamer.process_streamer()
                if len(processData) > 1:
                    await self.channel.send(processData)

            print("Twitch and goodgame have been read")
            log.info("Twitch and goodgame have been read")
            await asyncio.sleep(60)

        # async with aiohttp.ClientSession() as session:
        #     while self.running:
        #         for streamer in self.streamers:
        #             try:
        #                 async with session.get(
        #                     "https://api.twitch.tv/helix/streams?user_login=" + streamer,
        #                     timeout=10,
        #                     headers=self.headers) as resp:

        #                     stream_data = await resp.json()

        #                     if not stream_data['data'] and streamer in self.streamer_live:
        #                         self.streamer_live.remove(streamer)

        #                     if stream_data['data'] and streamer not in self.streamer_live:
        #                         await self.channel.send("@everyone\n{0} is online".format(streamer))
        #                         self.streamer_live.append(streamer)

        #             except Exception as e:
        #                 print("Failed to load twitch: {}".format(repr(e)))
        #                 log.warning("Failed to load twitch: {}".format(repr(e)))

        #             await asyncio.sleep(5)

        #         for goodgame_stream in self.goodgame:
        #             try:
        #                 async with session.get(
        #                     "http://goodgame.ru/api/getggchannelstatus?id=" + goodgame_stream + "&fmt=json", 
        #                     timeout=10) as resp:

        #                     data = await resp.json()

        #                     if data[goodgame_stream]["status"] == "Live" and goodgame_stream not in self.goodgames_live:
        #                         self.goodgames_live.append(goodgame_stream)
        #                         await self.channel.send("@everyone\n{0} is online".format(self.goodgame[goodgame_stream]))

        #                     if data[goodgame_stream]["status"] == "Dead" and goodgame_stream in self.goodgames_live:
        #                         self.goodgames_live.remove(goodgame_stream)

        #             except Exception as e:
        #                 log.warning("Goodgame timed out: {}".format(repr(e)))
        #                 print("Goodgame timed out: {}".format(repr(e)))

        #             await asyncio.sleep(5)

        #         print("Twitch and goodgame have been read")
        #         log.info("Twitch and goodgame have been read")
        #         await asyncio.sleep(60)


if __name__ == "__main__":
    s = StreamerFeeder(None)
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(get_channel_by_name("forsen"))
    # loop.run_until_complete(get_channel_by_name("lasqa"))
    loop.run_until_complete(s.feed())
