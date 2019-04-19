import random
import aiohttp

import logging
log = logging.getLogger(__name__)

class Proxy:
    def __init__(self):
        self.proxyDict = []
        self.current = None

    def changeCurrent(self):
        self.current = random.choice(self.proxyDict)
    
    async def get_new(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=1000&anonymity=all&ssl=yes") as resp:
                    data = await resp.text()
                    proxiesRaw = data.split('\r\n')
                    del proxiesRaw[-1] # last is always empty
                
                    self.proxyDict = []
                    for i in range(len(proxiesRaw)):
                        dic = 'http://' + proxiesRaw[i]
                        #dic = {"http":proxiesRaw[i], "https":proxiesRaw[i]}
                        self.proxyDict.append(dic)
                    self.current = random.choice(self.proxyDict)
                    log.info("Proxies loaded. Size: {}".format(len(proxiesRaw)))
                    print("Proxies loaded. Size: {}".format(len(proxiesRaw)))
            except Exception as e:
                print("Error while loading proxy list: {}".format(repr(e)))
                log.warning("Error while loading proxy list: {}".format(repr(e)))
