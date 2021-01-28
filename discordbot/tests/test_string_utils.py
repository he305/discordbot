from discordbot.utils.string_utils import StringUtills
import re


class TestStringUtils:
    def test_fix_rss_title(self):
        st1 = StringUtills.fix_rss_title('Steins;Gate 0 - 01 [1080p].mkv')
        assert(st1 == 'steins gate')
        st2 = StringUtills.fix_rss_title('Kaifuku Ju - 03 [VRV][1080p].mkv')
        assert(st2 == 'kaifuku ju')

    def test_remove_characters(self):
        st = StringUtills.remove_characters('s;4;1;i&w(23%2')
        assert (st == 's 4 1 i w 23')

    def test_rss_pattern(self):
        pattern = StringUtills.rss_pattern
        st1 = 'Steins;Gate 0 - 01 [1080p].mkv'
        assert(re.match(pattern, st1).group(1) == 'Steins;Gate 0')
        st2 = 'Kaifuku Ju - 03 [VRV][1080p].mkv'
        assert(re.match(pattern, st2).group(1) == 'Kaifuku Ju')
