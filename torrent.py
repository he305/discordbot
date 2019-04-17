import requests
import asyncio
from urllib.parse import urlparse
import shutil
from hidden_data import USER_TORRENT, PASSWORD_TORRENT
import transmissionrpc
from tempfile import NamedTemporaryFile
import os


import logging
log = logging.getLogger(__name__)

class Torrent:
    def __init__(self, proxy):
        self.proxy = proxy
        self.tc = transmissionrpc.Client('localhost', port=9091, user=USER_TORRENT, password=PASSWORD_TORRENT)
        print("Torrent loaded")
        log.info("Torrent loaded")

    async def add_torrent(self, url):
        total, used, free = shutil.disk_usage("/")
        if free // (2**30) < 2:
            print("No free space left, can't add torrent")
            log.warning("No free space left, can't add torrent")
            return False
        
        parsed_url = urlparse(url)

        i = 0
        temp_file = None
        while temp_file is None:
            try:
                req = requests.get(url, timeout=5, proxies=self.proxy.current)
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if i > 5:
                    self.proxy.get_new()
                    i = 0
                print("Failed to load torrent")
                log.warning("Failed to torrent")
                self.proxy.changeCurrent()
                i += 1
                await asyncio.sleep(5)
            else:
                if (req.status_code != 200):
                    print("Nyaa.si is probably down, failed to load torrent")
                    log.warning("Nyaa.si is probably down, failed to load torrent")
                    return False
                else: 
                    url_name = parsed_url.path.split('/')[-1]
                    temp_file = NamedTemporaryFile(prefix=url_name, delete=False)

                    with open(temp_file, 'wb') as f:
                        f.write(req.content)
            
        try:
            self.tc.add_torrent(temp_file)
        except Exception as e:
            print("Error while adding torrent: {}".format(e))
            log.warning("Error while adding torrent: {}".format(e))
            return False

        print("Successfully added torrent: {}".format(url))
        log.info("Successfully added torrent: {}".format(url))
        os.remove(temp_file)
        return True