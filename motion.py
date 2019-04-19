import asyncio
import glob
import discord
import datetime

import logging
log = logging.getLogger(__name__)


class Motion:
    def __init__(self, client):
        self.client = client
        self.motion_dir = '/home/pi/motion/'
        self.cached_images = []
        self.running = False
        self.channel = ""

    async def feed(self):
        await self.client.wait_until_ready()
        for server in self.client.guilds:
            for channel in server.channels:
                if channel.name == "motion":
                    self.channel = channel
                    break
        
        files = [f for f in glob.glob(self.motion_dir + "*.jpg")]
        files.sort()

        for f in files:
            name = f.split('/')[-1].replace('.jpg', '')
            date = datetime.datetime.strptime(name, '%m:%d_%H:%M:%S').replace(year=datetime.datetime.today().year)
            if (datetime.datetime.today() - date).seconds > 120:
                self.cached_images.append(f)
            
        self.running = True
        print("Motion started to work")
        log.info("Motion started to work")
        self.client.loop.create_task(self.get_images())

    async def get_images(self):
        while self.running:
            files = [f for f in glob.glob(self.motion_dir + "*.jpg")]

            files.sort()
            for f in files:
                if f not in self.cached_images:
                    await self.channel.send(file=discord.File(f))
                    self.cached_images.append(f)

            await asyncio.sleep(30)