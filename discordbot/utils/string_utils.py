import re


class StringUtills:
    rss_pattern = r'(^[a-zA-Z0-9\s!\'@#$%^&*()\[\]\{\}\;\:\,\.\/\<\>\?\|\`\~\-\–\=\_\+]*) [-–] \d+'

    @staticmethod
    def delete_season_patter(st):
        # delete_season_pattern
        st = re.sub('\s+\d+$', '', st)
        return st

    @staticmethod
    def remove_characters(st):
        """
        Replace all special characters for spaces
        :param st: string to be replaced
        :return:
        """
        st = st.translate({ord(c): " " for c in "'!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).lower()
        st = StringUtills.delete_season_patter(st)
        return " ".join(st.split())

    @staticmethod
    def fix_rss_title(st):
        """
        Fix horriblesubs title for comprasion with mal titles
        Example: Steins;Gate 0 - 01 [1080p].mkv -> steins gate
        :param st: string to be fixed
        :return:
        """
        pattern = StringUtills.rss_pattern
        try:
            title = StringUtills.remove_characters(re.match(pattern, st).group(1))
            return title
        except AttributeError:
            print("Attribute error: " + st)
            return st
