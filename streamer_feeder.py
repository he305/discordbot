import requests
import asyncio
import os
import json

from vk_api import get_new_posts

CLIENT_ID = os.environ.get('CLIENT_ID') or "jc9acocupd7auyfhcpaxjv5o5dckh5"

class StreamerFeeder:
    def __init__(self, client):
        self.client = client
        self.streamers = []
        self.groups = {}

        self.group_posts = []
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

                if res in self.group_posts:
                    await asyncio.sleep(300)
                    continue

                self.group_posts.append(res)

                if len(self.group_posts) > 1:
                    print(self.group_posts[0])
                    print(self.group_posts[1])

                url = ""
                if 'attachments' in res:
                    for att in res['attachments']:
                        if att['type'] == 'photo':
                            url = att['photo']['photo_1280']
                text = ""
                if 'text' in res:
                    text = res['text']
                data = "@everyone\n{}{}{}".format(self.groups[group], '\n' + text, '\n' + url)

                await self.client.send_message(self.channel, data)

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
                    await self.client.send_message(self.channel, "@everyone/n{0} is online".format(streamer))
                    self.streamers[self.streamers.index(streamer)] = streamer + '_live'

                await asyncio.sleep(60)
if __name__ == "__main__":
    s = StreamerFeeder(None)

    s.feed()