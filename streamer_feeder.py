import requests
import asyncio
import os

CLIENT_ID = os.environ.get('CLIENT_ID') or "jc9acocupd7auyfhcpaxjv5o5dckh5"

class StreamerFeeder:
    def __init__(self, client):
        self.client = client
        self.streamers = []
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

        for streamer in self.streamers:
            print(streamer)

        for server in self.client.servers:
            for channel in server.channels:
                if channel.name == "streamer-feed":
                    self.channel = channel
                    break

        self.running = True
        self.client.loop.create_task(self.feed_loop())

    async def feed_loop(self):
        while self.running:
            for streamer in self.streamers:
                stream_data = requests.get(
                    "https://api.twitch.tv/helix/streams?user_login=" + streamer.replace('_live', ''),
                    headers=self.headers).json()

                if not stream_data['data'] and '_live' in streamer:
                    self.streamers[self.streamers.index(streamer)] = streamer.replace('_live', '')

                if stream_data['data'] and '_live' not in streamer:
                    await self.client.send_message(self.channel, "{0} is online".format(streamer))
                    self.streamers[self.streamers.index(streamer)] = streamer + '_live'

                await asyncio.sleep(60)
if __name__ == "__main__":
    s = StreamerFeeder(None)

    s.feed()