from dateutil.parser import parse
import aiohttp
from bs4 import BeautifulSoup

import logging
log = logging.getLogger(__name__)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

days = [
    'понедельник',
    'вторник',
    'среду',
    'четверг',
    'пятницу',
    'субботу',
    'воскресенье'
]


class Info:
    def __init__(self, anime):
        # Collecting info
        self.id = int(anime["anime_id"])
        self.name = anime['anime_title']
        self.watched = int(anime["num_watched_episodes"])
        self.watching_status = int(anime["status"])
        self.score = int(anime["score"])

        # Used for cases when date is in broken format, e.g. 04-00-21. Can parse it, but if starting date is undefined it's not useful anyway.
        try:
            self.start = parse(anime['anime_start_date_string']).date()
            self.weekday = self.start.weekday()
        except ValueError:
            self.start = parse("01-01-2021").date()
            self.weekday = self.start.weekday()

        if 'series_synonyms' in anime:
            self.synonyms = [c.strip() for c in anime['series_synonyms'].split(';')]
        else:
            self.synonyms = []

        if 'anime_image_path' in anime:
            self.image = anime['anime_image_path']
        else:
            self.image = ""

        # Kept for better days
        if anime['anime_airing_status'] == '2':
            #all_eps = int(anime['total_episodes'])
            self.status = 'ended'
        else:
            #data = requests.get("https://api.jikan.moe/v3/anime/{}/episodes".format(anime["mal_id"]), timeout=10, headers=headers).json()
            #all_eps = len(data["episodes"])
            self.status = 'airing'

        #self.series_count = all_eps

    def form_full_info(self):
        info = ''
        info += '{0} - {1} серий\n'.format(self.name, str(self.watched))
        # if self.series_count - self.watched != 0:
        #     info += '{0} пропущено\n'.format(str(self.series_count - self.watched))
        if self.status == 'airing':
            info += 'Новая серия в {0}.\n'.format(days[self.weekday])
        info += self.image
        return info

    def get_all_names(self):
        return self.name + ' ' + " ".join(self.synonyms)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Info):
            return self.name == other.name and self.watching_status == other.watching_status
        return False

    async def get_synonyms(self):
        async with aiohttp.ClientSession() as session:
            i = 0
            while not self.synonyms:
                try:
                    async with session.get("https://myanimelist.net/anime/{}".format(self.id), timeout=5) as resp:
                        soup = BeautifulSoup(await resp.text(), 'html.parser')

                        td = soup.find("td", class_="borderClass")
                        divs = td.find_all("div", class_="spaceit_pad")

                        if divs:
                            for div in divs:
                                self.synonyms.append(div.contents[2].strip())
                        print("Synonyms for {} loaded".format(self.name))
                        log.info("Synonyms for {} loaded".format(self.name))
                except Exception as e:
                    print("Error getting anime synonyms: {}".format(repr(e)))
                    log.warning("Error getting anime synonyms: {}".format(repr(e)))
                    if i > 5:
                        break
                    i += 1


class InfoRaw:
    def __init__(self, anime):
        self.name = anime

    def get_all_names(self):
        return self.name

    def __str__(self):
        return self.name

    def form_full_info(self):
        return self.name + '\n'
