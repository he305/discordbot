import aiohttp
import asyncio
import requests
from hidden_data import LOGIN_MAL, PASS_MAL
from dateutil.parser import isoparse

import logging
log = logging.getLogger(__name__)

class MALAPIV1:
    nickaname = 'he3050'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
    
    @staticmethod
    async def get_anime_list():
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://myanimelist.net/animelist/{}/load.json?offset=0".format(MALAPIV1.nickaname), timeout=10, headers=MALAPIV1.headers) as resp:
                    raw_data = await resp.read()

                data = json.loads(raw_data)
                return data
            except Exception as e:
                print("Error while loading anime data: {}".format(repr(e)))
                log.warning("Error while loading anime data: {}".format(repr(e)))
                return []


class MALAPIV2b:
    ACCESS_TOKEN = None
    headers = {
        "Host": "api.myanimelist.net",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
    }
    login = LOGIN_MAL
    passwd = PASS_MAL

    @staticmethod
    async def __get_access_token():
        URL = "https://api.myanimelist.net/v2/auth/token"
        headers= {
            "Host": "api.myanimelist.net",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
            "Content-Length": "112",
        }
        data = "grant_type=password&client_id=6114d00ca681b7701d1e15fe11a4987e&password={}&username={}".format(MALAPIV2b.passwd, MALAPIV2b.login)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    URL,
                    timeout=3,
                    headers=headers,
                    data = data) as resp:

                    loginData = await resp.json()
        except Exception:
            # TODO
            loginData = requests.post(URL, headers=headers, data=data).json()
        
        if 'access_token' not in loginData:
            log.warning("Can't login to MAL, error: {}, message: {}".format(loginData['error'], loginData['message']))
            return None

        return loginData["access_token"]

    @staticmethod
    async def get_anime_list(fields=["alternative_titles", "broadcast", "status", "start_date", "my_list_status", "num_episodes"], sort="", limit=100, offset=0):
        if MALAPIV2b.ACCESS_TOKEN is None:
            token = await MALAPIV2b.__get_access_token()
            if token is None:
                log.warning("Couldn't get anime list, returning None")
                return None
            MALAPIV2b.ACCESS_TOKEN = token

        if not fields:
            URL = "https://api.myanimelist.net/v2/users/@me/animelist?limit={}&offset={}&sort={}".format(limit, offset, sort)
        else:
            query = "&fields="
            for field in fields:
                query += (field + ",")
            URL = "https://api.myanimelist.net/v2/users/@me/animelist?limit={}&offset={}&sort={}".format(limit, offset, sort) + query[:-1]

        headers = MALAPIV2b.headers
        headers["Authorization"] = "Bearer {}".format(MALAPIV2b.ACCESS_TOKEN)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    URL,
                    timeout=3,
                    headers=headers) as resp:

                    response = await resp.json()
        except Exception:
            # TODO
            response = requests.get(URL, headers=headers).json()

        nextPage = response['paging']

        # While the next field in response is not empty, keep sending request for next page
        #print(json.dumps(response["data"], sort_keys=True, indent=4))
        animeList = response["data"]
        while 'next' in nextPage:
            nextURL = nextPage['next']
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        nextURL,
                        timeout=3,
                        headers=headers) as resp:

                        nextResponse = await resp.json()
            except Exception:
                # TODO
                nextResponse = requests.get(nextURL, headers=headers).json()
            for entry in nextResponse["data"]:
                animeList.append(entry)
                
            nextPage = nextResponse['paging']
        return animeList

    # def getAnimeListStatus(self, ACCESS_TOKEN, status, fields=[], sort="", limit=100, offset=0):
    #         if not fields:
    #             URL = "https://api.myanimelist.net/v2/users/@me/animelist?status={}&limit={}&offset={}&sort={}".format(status, limit, offset, sort)
    #         else:
    #             query = "&fields="
    #             for field in fields:
    #                 query += (field + ",")
    #             URL = "https://api.myanimelist.net/v2/users/@me/animelist?status={}&limit={}&offset={}&sort={}".format(status, limit, offset, sort) + query[:-1]

    #         headers = REQUEST_HEADERS
    #         headers["Authorization"] = "Bearer {}".format(ACCESS_TOKEN)
    #         response = requests.get(URL, headers = headers).json()
    #         nextPage = response['paging']

    #         # While the next field in response is not empty, keep sending request for next page
    #         animeList = [response]
    #         while 'next' in nextPage:
    #             nextURL = nextPage['next']
    #             nextResponse = requests.get(nextURL, headers = headers).json()
    #             animeList.append(nextResponse)
    #             nextPage = nextResponse['paging']
    #         return animeList

    # def myInfo(self, ACCESS_TOKEN, fields=[]):
    #         if not fields:
    #             URL = "https://api.myanimelist.net/v2/users/@me"
    #         else:
    #             query = "?fields="
    #             for field in fields:
    #                 query += (field + ",")
    #             URL = "https://api.myanimelist.net/v2/users/@me" + query[:-1]

    #         headers = REQUEST_HEADERS
    #         headers["Authorization"] = "Bearer {}".format(ACCESS_TOKEN)

    #         stats = requests.get(URL, headers = headers).json()
    #         return stats

import json

async def main():
    full_list = await MALAPIV2b.get_anime_list(limit=100)
    # with open("test.json", 'w') as file_data:
    #     json.dump(full_list, file_data)

    for node in full_list:
        if (node["node"]['status'] == 'not_yet_aired'): #finished_airing
            print(json.dumps(node["node"], sort_keys=True, indent=4))
            return
    #print(json.dumps(full_list[0]['node'], sort_keys=True, indent=4))
    #print(json.dumps(await API.getAnimeList(["alternative_titles", "broadcast", "status", "start_date", "my_list_status"], limit=100), sort_keys=True, indent=4))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    #print(json.dumps(API.getAnimeList(["alternative_titles", "broadcast", "status", "start_date", "my_list_status"], limit=100), sort_keys=True, indent=4))

# import secrets

# def get_new_code_verifier() -> str:
#     token = secrets.token_urlsafe(100)
#     return token[:128]

# code_verifier = code_challenge = get_new_code_verifier()

# print(len(code_verifier))
# print(code_verifier)
