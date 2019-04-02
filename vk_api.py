import requests

from hidden_data import ACCESS_TOKEN

def send_message(message):
    r = requests.get("https://api.vk.com/method/messages.send?user_id=420339262&message={}&v=5.84&access_token={}".format(message, ACCESS_TOKEN)).json()
    print(r)

def get_new_posts(group):
    r = requests.get("https://api.vk.com/method/wall.get?count=2&owner_id=-{}&v=5.84&access_token={}".format(group, ACCESS_TOKEN)).json()
    if 'is_pinned' in r['response']['items'][0]:
        return r['response']['items'][1]
    return r['response']['items'][0]

def get_post_comments(group, post_id):
    r = requests.get("https://api.vk.com/method/wall.getComments?count=100&need_likes=1&owner_id=-{}&post_id={}&v=5.84&access_token={}".format(group, post_id, ACCESS_TOKEN)).json()

    count = int(r['response']['count'])
    if count < 100:
        items = r['response']['items']
    else:
        items = r['response']['items']
        k = 100
        while k < count:
            r = requests.get("https://api.vk.com/method/wall.getComments?count=100&offset={}&need_likes=1&owner_id=-{}&post_id={}&v=5.84&access_token={}".format(k, group, post_id, ACCESS_TOKEN)).json()
            items = items + r['response']['items']
            k += 100 
    return items
