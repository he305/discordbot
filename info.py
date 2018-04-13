from lxml import etree
import datetime
import math


days = [
    'понедельник',
    'вторник',
    'среду',
    'четверг',
    'пятницу',
    'субботу',
    'воскресенье'
];

class Info:
    def __init__(self, anime):
        #Collecting info
        self.name = anime.find('series_title').text
        self.watched = int(anime.find('my_watched_episodes').text)
        #date format - 2002-10-03
        self.start = datetime.datetime.strptime(anime.find('series_start').text, "%Y-%m-%d").date()
        self.weekday = self.start.weekday()
        print(self.name)
        if anime.find('series_synonyms').text is not None:
            self.synonyms = [c.strip() for c in anime.find('series_synonyms').text.split(';')]
        else:
            self.synonyms = []
        all_eps = 0
        
        if anime.find('series_status').text == '2':
            all_eps = int(anime.find('series_episodes').text)
            self.status = 'ended'
        else:
            today = datetime.date.today()
            all_eps = math.floor((today - self.start).days/7)+1
            self.status = 'airing'

        self.series_count = all_eps

    def form_full_info(self):
        info = ''
        info += '{0} - {1} серий\n'.format(self.name, str(self.watched))
        if self.series_count - self.watched != 0:
            info += '{0} пропущено\n'.format(str(self.series_count - self.watched))
        if self.status == 'airing':
            info += 'Новая серия в {0}.\n'.format(days[self.weekday])
        return info

    def is_skipped(self):
        return self.series_count - self.watched

    def get_all_names(self):
        return self.name + ' ' + " ".join(self.synonyms)

    def __str__(self):
        return self.name