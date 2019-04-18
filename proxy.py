import random
import requests

import logging
log = logging.getLogger(__name__)

class Proxy:
    def __init__(self):
        self.proxyDict = []
        self.current = None
        self.get_new()

    def changeCurrent(self):
        self.current = random.choice(self.proxyDict)
    
    def get_new(self):
        proxiesRaw = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=3000&anonymity=all&ssl=yes").text.split('\r\n')
        del proxiesRaw[-1] # last is always empty
      
        self.proxyDict = []
        for i in range(len(proxiesRaw)):
            dic = 'http://' + proxiesRaw[i]
            #dic = {"http":proxiesRaw[i], "https":proxiesRaw[i]}
            self.proxyDict.append(dic)
        self.current = random.choice(self.proxyDict)
        log.info("Proxies loaded. Size: {}".format(len(proxiesRaw)))
        print("Proxies loaded. Size: {}".format(len(proxiesRaw)))
