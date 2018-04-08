import sys
import requests
import json

API_URL = "http://api.openweathermap.org/data/2.5/"
DEFAULT_CITY = "Elektrostal,RU"
APP_ID = "37dee516c076d97ff41c640458563769"

def get_location_data():
    location = requests.get("http://freegeoip.net/json")
    return json.loads(location.text) 

def weather():
    location_data = get_location_data()
    lat = location_data['latitude']
    lon = location_data['longitude']
    params = {
        'type' : 'like',
        'units' : 'metric',
        'appid' : APP_ID,
        'lat' : lat,
        'lon' : lon
    }

    res = requests.get(API_URL+'weather', params=params)
    data = res.json()
    print("Weather for {0}/{1}".format(location_data['country_name'], location_data['city']))
    return data


def forecast():
    location_data = get_location_data()
    lat = location_data['latitude']
    lon = location_data['longitude']
    params = {
        'type' : 'like',
        'units' : 'metric',
        'appid' : APP_ID,
        'lat' : lat,
        'lon' : lon
    }

    res = requests.get(API_URL+'forecast', params=params)
    data = res.json()
    print("Forecast for {0}/{1}".format(location_data['country_name'], location_data['city']))
    for i in data['list']:
        print(i['dt_txt'], '{0:3.0f}'.format(i['main']['temp']), i['weather'][0]['description'])

def main():
    if len(sys.argv) == 1:
        weather()
    elif sys.argv[1] == "forecast":
        forecast()

if __name__ == "__main__":
    main()