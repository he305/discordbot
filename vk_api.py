import requests
import os
import datetime

from time import sleep

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

def send_message(message):
    r = requests.get("https://api.vk.com/method/messages.send?user_id=420339262&message={}&v=5.52&access_token={}".format(message, ACCESS_TOKEN)).json()
    print(r)

def get_new_posts(group):
    r = requests.get("https://api.vk.com/method/wall.get?count=1&owner_id=-{}&v=5.52&access_token={}".format(group, ACCESS_TOKEN)).json()
    return r['response']['items'][0]

