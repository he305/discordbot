import requests
import os
import datetime

from time import sleep

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

def send_message(message):
    r = requests.get("https://api.vk.com/method/messages.send?user_id=420339262&message={}&v=5.52&access_token={}".format(message, ACCESS_TOKEN)).json()
    print(r)

def get_new_posts(group):
    r = requests.get("https://api.vk.com/method/wall.get?count=2&owner_id=-{}&v=5.52&access_token={}".format(group, ACCESS_TOKEN)).json()
    if 'is_pinned' in r['response']['items'][0]:
        return r['response']['items'][1]
    return r['response']['items'][0]

# from pprint import pprint
# d = get_new_posts(98944499)
# import time

# cur = time.time()

# print((cur - int(d['date'])))
# data = []

# i = 0
# while True:
#     res = get_new_posts(98839886)
#     print("It {}, length {}".format(i, len(data)))
#     i += 1
    
#     if res in data:
#         sleep(10)
#         continue
#     data.append(res)

#     if len(data) > 1:
#         print(data[0])
#         print(data[1])
#         break
    
#     print("It {}, length {}".format(i, len(data)))
#     sleep(10)