from dateutil.parser import isoparse
import aiohttp
import asyncio
from bs4 import BeautifulSoup

import logging
log = logging.getLogger(__name__)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

watching_status_enum = {
    'watching': 1,
    'completed': 2,
    'on_hold': 3,
    'dropped': 4,
    'plan_to_watch': 6
}

days = [
    'понедельник',
    'вторник',
    'среду',
    'четверг',
    'пятницу',
    'субботу',
    'воскресенье'
]


class InfoRaw:
    def __init__(self, anime):
        self.name = anime

    def get_all_names(self):
        return self.name

    def __str__(self):
        return self.name

    def form_full_info(self):
        return self.name + '\n'

    def __eq__(self, other):
        if isinstance(other, InfoRaw):
            return self.name == other.name  # and self.watching_status == other.watching_status
        return False


class InfoMALv1(InfoRaw):
    def __init__(self, anime):
        # Collecting info
        self.id = int(anime["anime_id"])
        self.name = anime['anime_title']
        self.watched = int(anime["num_watched_episodes"])
        self.watching_status = int(anime["status"])
        self.score = int(anime["score"])

        # Used for cases when date is in broken format, e.g. 04-00-21.
        # Can parse it, but if starting date is undefined
        # it's not useful anyway.
        # 25.01.2021 - probably fixed with isoparse
        try:
            self.start = isoparse(anime['anime_start_date_string']).date()
            self.weekday = self.start.weekday()
        except ValueError:
            self.start = isoparse("2021-01-01").date()
            self.weekday = self.start.weekday()

        if 'series_synonyms' in anime:
            self.synonyms = [c.strip() for c in anime['series_synonyms'].split(';')]
        else:
            self.synonyms = []

        if 'anime_image_path' in anime:
            self.image = anime['anime_image_path']
        else:
            self.image = ""

        if anime['anime_airing_status'] == '2':
            self.status = 'ended'
        else:
            self.status = 'airing'

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
        if isinstance(other, InfoMALv1):
            return self.name == other.name and self.watching_status == other.watching_status
        return False

    async def get_synonyms(self):
        async with aiohttp.ClientSession() as session:
            i = 0
            while not self.synonyms:
                try:
                    async with session.get("https://myanimelist.net/anime/{}"
                                           .format(self.id), timeout=5) as resp:

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
        # Bad code
        await asyncio.sleep(3)


class InfoMALv2b(InfoRaw):
    def __init__(self, anime):
        # Collecting info
        self.id = int(anime['id'])
        self.name = anime['title']
        self.watched = int(anime['my_list_status']['num_episodes_watched'])
        watching_status_str = anime['my_list_status']['status']
        self.watching_status = watching_status_enum[watching_status_str]
        self.score = int(anime['my_list_status']['score'])

        if 'start_date' in anime:
            self.start = isoparse(anime['start_date']).date()
            self.weekday = self.start.weekday()

        if 'alternative_titles' in anime:
            alt_titles = anime['alternative_titles']
            self.synonyms = []
            if 'en' in alt_titles:
                self.synonyms.append(alt_titles['en'])
            if 'ja' in alt_titles:
                self.synonyms.append(alt_titles['ja'])
            if 'synonyms' in alt_titles:
                for c in alt_titles['synonyms']:
                    self.synonyms.append(c.strip())

        if 'main_picture' in anime:
            self.image = anime['main_picture']['large']
        else:
            self.image = ""

        self.num_episodes = anime['num_episodes']

        self.status = anime['status']

    def form_full_info(self):
        info = ''
        info += '{0} - {1} серий\n'.format(self.name, str(self.watched))
        if self.num_episodes - self.watched != 0:
            info += '{0} пропущено\n'.format(str(self.num_episodes - self.watched))
        if self.status == 'airing':
            info += 'Новая серия в {0}.\n'.format(days[self.weekday])
        info += self.image
        return info

    def get_all_names(self):
        return self.name + ' ' + " ".join(self.synonyms)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, InfoMALv2b):
            return self.name == other.name and self.watching_status == other.watching_status
        return False

    async def get_synonyms(self):
        pass
