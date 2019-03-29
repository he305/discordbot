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
]


class Info:
    def __init__(self, anime):
        # Collecting info
        self.name = anime['title']
        self.watched = int(anime["watched_episodes"])
        # date format - 2002-10-03
        self.start = datetime.datetime.strptime(anime['start_date'], "%Y-%m-%dT%H:%M:%S%z").date()
        self.weekday = self.start.weekday()
        if anime['series_synonyms'] is not None:
            self.synonyms = [c.strip() for c in anime['series_synonyms'].split(';')]
        else:
            self.synonyms = []

        if anime['airing_status'] == '2':
            all_eps = int(anime['total_episodes'])
            self.status = 'ended'
        else:
            today = datetime.date.today()
            all_eps = math.floor((today - self.start).days / 7) + 1
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


class InfoRaw:
    def __init__(self, anime):
        self.name = anime

    def get_all_names(self):
        return self.name

    def __str__(self):
        return self.name

    def form_full_info(self):
        return self.name + '\n'