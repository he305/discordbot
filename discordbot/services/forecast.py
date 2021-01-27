import json

import requests

API_URL = "http://api.openweathermap.org/data/2.5/"
DEFAULT_CITY = "Elektrostal"
APP_ID = "37dee516c076d97ff41c640458563769"


def get_location_data():
    location = requests.get("http://freegeoip.net/json")
    return json.loads(location.text)


def weather():
    params = {
        'type': 'like',
        'units': 'metric',
        'appid': APP_ID,
        'q': DEFAULT_CITY
    }

    res = requests.get(API_URL + 'weather', params=params)
    data = res.json()
    location = "Weather for {}\n".format(DEFAULT_CITY)
    str_data = "{0}°/{1}° - {2}\n".format(data["main"]["temp_min"], data["main"]["temp_max"],
                                          data["weather"][0]["description"])
    return location + str_data


def forecast():
    location_data = get_location_data()
    params = {
        'type': 'like',
        'units': 'metric',
        'appid': APP_ID,
        'q': DEFAULT_CITY
    }

    res = requests.get(API_URL + 'forecast', params=params)
    data = res.json()
    print("Forecast for {0}/{1}".format(location_data['country_name'], location_data['city']))
    for i in data['list']:
        print(i['dt_txt'], '{0:3.0f}'.format(i['main']['temp']), i['weather'][0]['description'])
