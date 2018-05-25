from lxml import etree
import urllib.request
import requests
from info import Info, InfoRaw


def get_watching_anime(xml):
    watching_anime = []
    for child in xml[1:]:
        if child.find("my_status").text == "1":
            watching_anime.append(child)
    return watching_anime


def get_url(url):
    return urllib.request.urlopen(url).read()


def get_data(nickaname):
    if nickaname is None:
        nickaname = 'he3050'

    anime_data = []
    data = requests.get("https://myanimelist.net/malappinfo.php?u={}&status=all".format(nickaname))
    if data.status_code == 404:
        data = requests.get("https://shikimori.org/he3050/list_export/animes.json").json()
        for ur in data:
            if ur["status"] == "watching":
                anime_data.append(InfoRaw(ur["target_title"]))
    else:
        root = etree.fromstring(data)
        watching_anime = get_watching_anime(root)

        for child in watching_anime:
            anime_data.append(Info(child))

    return anime_data


def main():
    data = get_data(None)

    for d in data:
        print(d.form_full_info())


if __name__ == "__main__":
    main()
