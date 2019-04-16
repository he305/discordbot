import requests
import asyncio
import json
import time

from vk_api import get_new_posts

from hidden_data import CLIENT_ID
MIN_LIKES = 10

import logging
log = logging.getLogger(__name__)

class StreamerFeeder:
    def __init__(self, client):
        self.client = client
        self.streamers = []
        self.goodgame = []
        self.goodgames_live = []
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

        with open('streamers.txt', 'r', encoding="utf8") as f:
            self.streamers = [s.strip() for s in f.readlines()]

        with open('groups.json', 'r', encoding="utf8") as f:
            self.groups = json.load(f)
        
        with open('goodgame.json', 'r', encoding="utf8") as f:
            self.goodgame = json.load(f)

        for streamer in self.streamers:
            print(streamer)

        for server in self.client.servers:
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
                res = get_new_posts(int(group))


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
                    await self.client.send_message(self.channel, data)
                
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
                #             await self.client.send_message(self.channel, data)



                await asyncio.sleep(300)

    async def feed_loop(self):
        while self.running:
            for streamer in self.streamers:
                stream_data = requests.get(
                    "https://api.twitch.tv/helix/streams?user_login=" + streamer.replace('_live', ''),
                    headers=self.headers).json()

                if not stream_data['data'] and '_live' in streamer:
                    self.streamers[self.streamers.index(streamer)] = streamer.replace('_live', '')

                if stream_data['data'] and '_live' not in streamer:
                    await self.client.send_message(self.channel, "@everyone\n{0} is online".format(streamer))
                    self.streamers[self.streamers.index(streamer)] = streamer + '_live'
        
            for goodgame_stream in self.goodgame:
                try:
                    data = requests.get("https://goodgame.ru/api/getggchannelstatus?id=" + goodgame_stream + "&fmt=json", timeout=10).json()
                    if data[goodgame_stream]["status"] == "Live" and goodgame_stream not in self.goodgames_live:
                        self.goodgames_live.append(goodgame_stream)
                        await self.client.send_message(self.channel, "@everyone\n{0} is online".format(self.goodgame[goodgame_stream]))

                    if data[goodgame_stream]["status"] == "Dead" and goodgame_stream in self.goodgames_live:
                        self.goodgames_live.remove(goodgame_stream)
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    print("Goodgame timed out")

            
            await asyncio.sleep(60)


if __name__ == "__main__":
    s = StreamerFeeder(None)

    s.feed()