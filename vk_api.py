import requests
import aiohttp

from hidden_data import ACCESS_TOKEN

import logging
log = logging.getLogger(__name__)


def send_message(message):
    r = requests.get("https://api.vk.com/method/messages.send?user_id=420339262&message={}&v=5.84&access_token={}".format(message, ACCESS_TOKEN)).json()
    print(r)


async def get_new_posts(group):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.vk.com/method/wall.get?count=2&owner_id=-{}&v=5.84&access_token={}".format(group, ACCESS_TOKEN)) as resp:
                data = await resp.json()
                if 'is_pinned' in data['response']['items'][0]:
                    return data['response']['items'][1]
                return data['response']['items'][0]
        except Exception as e:
            print("Error while getting new posts from vk group: {}".format(repr(e)))
            log.warning("Error while getting new posts from vk group: {}".format(repr(e)))


async def get_post_comments(group, post_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.vk.com/method/wall.getComments?count=100&need_likes=1&owner_id=-{}&post_id={}&v=5.84&access_token={}".format(group, post_id, ACCESS_TOKEN)) as resp:
                data = await resp.json()

                count = int(data['response']['count'])
                if count < 100:
                    items = data['response']['items']
                else:
                    items = data['response']['items']
                    k = 100
                    while k < count:
                        async with session.get("https://api.vk.com/method/wall.getComments?count=100&offset={}&need_likes=1&owner_id=-{}&post_id={}&v=5.84&access_token={}".format(k, group, post_id, ACCESS_TOKEN)) as r:
                            inner = await r.json()
                            items = items + inner['response']['items']
                            k += 100
                return items
        except Exception as e:
            print("Error while getting commentary from vk group: {}".format(repr(e)))
            log.warning("Error while getting commentary from vk group: {}".format(repr(e)))
