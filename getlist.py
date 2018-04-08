from lxml import etree
import urllib.request
from info import Info


def get_watching_anime(xml):
    watching_anime = []
    for child in xml[1:]:
        if (child.find("my_status").text == "1"):
            watching_anime.append(child)
    return watching_anime


def get_url(url):
    return urllib.request.urlopen(url).read()


def get_data(nickaname):
    if nickaname is None:
        nickaname = 'he3050'
    data = get_url("https://myanimelist.net/malappinfo.php?u={}&status=all".format(nickaname))
    root = etree.fromstring(data)
    watching_anime = get_watching_anime(root)
    anime_data = []
    for child in watching_anime:
        anime_data.append(Info(child))

    return anime_data


def main():
    data = get_data(None)

    for d in data:
        print(d.form_full_info())    


if __name__ == "__main__":
    main()