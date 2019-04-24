import aiohttp
from discord.ext import commands
from bs4 import BeautifulSoup
import asyncio

import logging
log = logging.getLogger(__name__)

headers = {
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "Content-Type" : "text/plain;charset=UTF-8"
}

class SearchImage(commands.Cog):
    def __init__(self, client):
        self.client = client

        print("Search ready")
        log.info("Search ready")

    @commands.command()
    async def s(self, ctx, url=None):
        if url == None:
            await ctx.send("No url image provided")
            return
        async with aiohttp.ClientSession() as session:
            site = "Google"
            try:
                async with session.get('https://www.google.com/searchbyimage?site=search&sa=X&image_url={}'.format(url), timeout=10, headers=headers) as resp:
                    soup = BeautifulSoup(await resp.text(), 'html.parser')
                    fina = soup.find_all("div", class_="r")
                    if len(fina) > 0:
                        await ctx.send('\n' + site)
                        for f in fina[:3]:
                            a = f.find("a")
                            await ctx.send(f.find("a")['href'] + '\n' + a.find("h3").text.strip())
                            await asyncio.sleep(1)
            except Exception as e:
                print("Exception while loading from {}: {}".format(site, repr(e)))
                log.warning("Exception while loading from {}: {}".format(site, repr(e)))

            site = "TineEye"
            try:
                async with session.get("http://tineye.com/search?url={}".format(url), timeout=10, headers=headers) as resp:
                    soup = BeautifulSoup(await resp.text(), 'html.parser')
                    fina = soup.find_all("div", class_="match")
                    if len(fina) > 0:
                        await ctx.send('\n' + site)
                        for f in fina[:3]:
                            p = f.find("p")
                            await ctx.send(p.find("a")['href'])
                            await asyncio.sleep(1)
            except Exception as e:
                print("Exception while loading from {}: {}".format(site, repr(e)))
                log.warning("Exception while loading from {}: {}".format(site, repr(e)))
            
            site = "Saucenao"
            try:
                async with session.get("https://saucenao.com/search.php?url={}".format(url), timeout=10, headers=headers) as resp:
                    soup = BeautifulSoup(await resp.text(), 'html.parser')
                    fina = soup.find_all("div", class_="resulttitle")
                    if len(fina) > 0:
                        await ctx.send('\n' + site)
                        for f in fina[:3]:
                            await ctx.send(f.text)
                            await asyncio.sleep(1)
            except Exception as e:
                print("Exception while loading from {}: {}".format(site, repr(e)))
                log.warning("Exception while loading from {}: {}".format(site, repr(e)))

            site = "iqdb"
            try:
                async with session.get("https://iqdb.org/?url={}".format(url), timeout=10, headers=headers) as resp:
                    soup = BeautifulSoup(await resp.text(), 'html.parser')
                    fina = soup.find_all("td", class_="image")
                    if len(fina) > 0:
                        await ctx.send('\n' + site)
                        for f in fina[1:4]:
                            a = f.find("a")
                            if 'http:' not in a['href']:
                                ur = 'http:' + a['href']
                            else: ur = a['href']
                            await ctx.send(ur + '\n' + a.find("img")['alt'])
                            await asyncio.sleep(1)
            except Exception as e:
                print("Exception while loading from {}: {}".format(site, repr(e)))
                log.warning("Exception while loading from {}: {}".format(site, repr(e)))

            await ctx.send("Search done")
            print("Search for {} done".format(url))
            log.info("Search for {} done".format(url))
            
