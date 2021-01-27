import asyncio
import json
import logging

from discordbot.utils.vk_api import get_new_posts
from discordbot.utils.streamer_utills import TwitchUtills
from discordbot.streamer.streamer_info import StreamerInfoTwitch, StreamerInfoWasd, StreamerInfoGoodgame

MIN_LIKES = 10

log = logging.getLogger(__name__)


class StreamerFeeder:
    def __init__(self, client):
        self.client = client
        self.streamers = []
        self.groups = {}

        self.group_posts = []
        self.comments = []
        self.running = False
        self.channel = None

    async def feed(self):
        await self.client.wait_until_ready()

        with open("configs/streamers.json", 'r', encoding='utf8') as f:
            streamers = json.load(f)

        for streamer in streamers["twitch"]:
            name = streamer["name"]
            if streamer["id"] is None:
                id = await TwitchUtills.get_channel_by_name(streamer["name"])
            else:
                id = streamer["id"]

            self.streamers.append(StreamerInfoTwitch(name, id))

        for streamer in streamers["wasd"]:
            self.streamers.append(StreamerInfoWasd(streamer["name"], streamer["id"]))

        for streamer in streamers["goodgame"]:
            self.streamers.append(StreamerInfoGoodgame(streamer["name"], streamer["id"]))

        for streamer in self.streamers:
            log.info(streamer)

        with open('configs/groups.json', 'r', encoding="utf8") as f:
            self.groups = json.load(f)

        for server in self.client.guilds:
            for channel in server.channels:
                if channel.name == "streamer-feed":
                    self.channel = channel
                    break

        self.running = True
        self.client.loop.create_task(self.feed_loop())
        # self.client.loop.create_task(self.group_feed_loop())

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
                try:
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
                except Exception as e:
                    log.info("Exception in streamer feeder, {}".format(e))
                    print("Exception in streamer feeder, {}".format(e))         

            print("Twitch and goodgame have been read")
            log.info("Twitch and goodgame have been read")
            await asyncio.sleep(60)
