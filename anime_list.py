from anime_info import Info
import aiohttp

#02.11.2018 found out that requests.get to shikimori returns 403 forbidden without user-agent header
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

import logging
log = logging.getLogger(__name__)

async def get_data(nickaname):
    if nickaname is None:
        nickaname = 'he3050'

    anime_data = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://myanimelist.net/animelist/{}/load.json?offset=0".format(nickaname), timeout=10, headers=headers) as resp:
                data = await resp.json()
                for ur in data:
                    anime_data.append(Info(ur))
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


def main():
    data = get_data(None)

    for d in data:
        print(d.form_full_info())


if __name__ == "__main__":
    main()
