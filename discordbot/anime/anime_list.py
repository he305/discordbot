from discordbot.anime.anime_info import InfoMALv1, InfoMALv2b, InfoRaw
import aiohttp
import json
import asyncio
from discordbot.utils.malapi import MALAPIV1, MALAPIV2b, SHIKIAPIV1
import discordbot.hidden_data as api_info
import logging
log = logging.getLogger(__name__)

# 02.11.2018 found out that requests.get to shikimori returns 403 forbidden without user-agent header
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


class AnimeListProvider:
    def __init__(self):
        self.api_list = {
            "MAL": {
                "V1": self.__get_anime_list_mal_v1,
                "V2b": self.__get_anime_list_mal_v2b
            },
            "SHIKI": {
                "V1": self.__get_anime_list_shiki_v1
            }
        }

    async def get_anime_list(self, nickname='he3050', ANIME_API=api_info.ANIME_API, API_VERSION=api_info.API_VERSION):
        try:
            return await self.api_list[ANIME_API][API_VERSION]()
        except Exception as e:
            log.warning("Error while loading anime data from {}, version {}: {}".format(ANIME_API, API_VERSION, repr(e)))
            return []

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
        anime_list = await SHIKIAPIV1.get_anime_list()
        data = []
        for ur in anime_list:
            data.append(InfoRaw(ur['target_title']))
        return data
