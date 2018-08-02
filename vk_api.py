import requests
import os

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

def send_message(message):
    r = requests.get("https://api.vk.com/method/messages.send?user_id=420339262&message={}&v=5.52&access_token={}".format(message, ACCESS_TOKEN)).json()
    print(r)
