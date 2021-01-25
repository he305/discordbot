from anime_info import InfoMALv1, InfoMALv2b
import aiohttp
import json
from malapi import MALAPIV1, MALAPIV2b
from hidden_data import ANIME_API, API_VERSION
import asyncio

#02.11.2018 found out that requests.get to shikimori returns 403 forbidden without user-agent header
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

import logging
log = logging.getLogger(__name__)

class AnimeListProvider:
    def __init__(self):
        self.api_list = {
            "MAL" : {
                "V1" : self.__get_anime_list_mal_v1,
                "V2b" : self.__get_anime_list_mal_v2b
            },
            "SHIKI" : {
                "V1" : self.__get_anime_list_shiki_v1
            }
        }
    
    async def get_anime_list(self, nickname='he3050'):
        return await self.api_list[ANIME_API][API_VERSION]()
            

    async def __get_anime_list_mal_v1(self):
        anime_list = await MALAPIV1.get_anime_list()
        data = []
        for ur in anime_list:
            data.append(InfoMALv1(ur))
        return data

    async def __get_anime_list_mal_v2b(self):
        anime_list = await MALAPIV2b.get_anime_list()
        data = []
        for ur in anime_list:
            data.append(InfoMALv2b(ur['node']))
        return data

    async def __get_anime_list_shiki_v1(self):
        pass

async def get_data(nickaname):


    if nickaname is None:
        nickaname = 'he3050'

    anime_data = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://myanimelist.net/animelist/{}/load.json?offset=0".format(nickaname), timeout=10, headers=headers) as resp:
                raw_data = await resp.read()

            data = json.loads(raw_data)
            for ur in data:
                anime_data.append(InfoMALv1(ur))
            return anime_data
        except Exception as e:
            print("Error while loading anime data: {}".format(repr(e)))
            log.warning("Error while loading anime data: {}".format(repr(e)))
            return [] 

    #Shikimori, just in case
    # try:
    #     data = requests.get("https://shikimori.org/{}/list_export/animes.json".format(nickaname), timeout=10, headers=headers).json()
    # except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    #     print("Shikimori down")
    #     return []
    # for ur in data:
    #     if ur["status"] == "watching":
    #         anime_data.append(InfoRaw(ur["target_title"]))


    return anime_data


async def main():

    provider = AnimeListProvider()
    data = await provider.get_anime_list()

    for d in data:
        if d.status == 'not_yet_aired':
            print(d.synonyms)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
