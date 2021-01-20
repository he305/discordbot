import asyncio
import aiohttp
from urllib.parse import urlparse
import shutil
from hidden_data import USER_TORRENT, PASSWORD_TORRENT
import transmissionrpc
from proxy import Proxy

import logging
log = logging.getLogger(__name__)


class Torrent:
    def __init__(self):
        try:
            self.tc = transmissionrpc.Client('localhost', port=9091, user=USER_TORRENT, password=PASSWORD_TORRENT)
        except Exception:
            print("Can't connect to transmission, torrent task won't work")
            log.warning("Can't connect to transmission, torrent task won't work")
            self.tc = None
            return

        self.proxy = Proxy()
        print("Torrent loaded")
        log.info("Torrent loaded")

    async def add_torrent(self, url):
        if self.tc is None:
            return False

        total, used, free = shutil.disk_usage("/")
        if free // (2**30) < 2:
            print("No free space left, can't add torrent")
            log.warning("No free space left, can't add torrent")
            return False

        await self.proxy.get_new()   
        parsed_url = urlparse(url)

        i = 0
        temp_file = None
        async with aiohttp.ClientSession() as session:
            while temp_file is None:
                try:
                    async with session.get(url, timeout=5, proxy=self.proxy.current) as resp:

                        if (resp.status != 200):
                            print("Nyaa.si is probably down, failed to load torrent")
                            log.warning("Nyaa.si is probably down, failed to load torrent")
                            return False
                        else:
                            url_name = parsed_url.path.split('/')[-1]

                            with open('tmp/' + url_name, 'wb') as temp_file:
                                temp_file.write(await resp.read())

                except Exception as e:
                    if i > 5:
                        await self.proxy.get_new()
                        i = 0
                    print("Failed to load torrent: {}".format(repr(e)))
                    log.warning("Failed to torrent: {}".format(repr(e)))
                    self.proxy.changeCurrent()
                    i += 1
                    await asyncio.sleep(5)

            try:
                self.tc.add_torrent('home/pi/git/discordbot/' + temp_file.name)
            except Exception as e:
                print("Error while adding torrent: {}".format(e))
                log.warning("Error while adding torrent: {}".format(e))
                return False

            print("Successfully added torrent: {}".format(url))
            log.info("Successfully added torrent: {}".format(url))
            #os.remove('home/pi/git/discordbot/' + temp_file.name)
            return True
