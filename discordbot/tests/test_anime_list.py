import pytest
from discordbot.anime.anime_list import AnimeListProvider

v1 = [{'status': 1, 'score': 0, 'tags': '', 'is_rewatching': 0, 'num_watched_episodes': 3, 'anime_title': '5-toubun no Hanayome ∬', 'anime_num_episodes': 12, 'anime_airing_status': 1, 'anime_id': 39783, 'anime_studios': None, 'anime_licensors': None, 'anime_season': None, 'has_episode_video': False, 'has_promotion_video': True, 'has_video': True, 'video_url': '/anime/39783/5-toubun_no_Hanayome_%E2%88%AC/video', 'anime_url': '/anime/39783/5-toubun_no_Hanayome_∬', 'anime_image_path': 'https://cdn.myanimelist.net/r/96x136/images/anime/1775/109514.jpg?s=cba7e1478072b27028c9932426c3c46b', 'is_added_to_list': False, 'anime_media_type_string': 'TV', 'anime_mpaa_rating_string': 'PG-13', 'start_date_string': None, 'finish_date_string': None, 'anime_start_date_string': '01-08-21', 'anime_end_date_string': None, 'days_string': None, 'storage_string': '', 'priority_string': 'Low'}, {'status': 1, 'score': 0, 'tags': '', 'is_rewatching': 0, 'num_watched_episodes': 4, 'anime_title': 'Hataraku Saibou Black (TV)', 'anime_num_episodes': 13, 'anime_airing_status': 1, 'anime_id': 41694, 'anime_studios': None, 'anime_licensors': None, 'anime_season': None, 'has_episode_video': False, 'has_promotion_video': True, 'has_video': True, 'video_url': '/anime/41694/Hataraku_Saibou_Black_TV/video', 'anime_url': '/anime/41694/Hataraku_Saibou_Black_TV', 'anime_image_path': 'https://cdn.myanimelist.net/r/96x136/images/anime/1837/110799.jpg?s=18cc22dc7a5eb78c3f0ae705f08487dc', 'is_added_to_list': False, 'anime_media_type_string': 'TV', 'anime_mpaa_rating_string': None, 'start_date_string': None, 'finish_date_string': None, 'anime_start_date_string': '01-10-21', 'anime_end_date_string': None, 'days_string': None, 'storage_string': '', 'priority_string': 'Low'}]
v2b = [{'node': {'id': 38101, 'title': '5-toubun no Hanayome', 'main_picture': {'medium': 'https://api-cdn.myanimelist.net/images/anime/1819/97947.jpg', 'large': 'https://api-cdn.myanimelist.net/images/anime/1819/97947l.jpg'}, 'alternative_titles': {'synonyms': ['Gotoubun no Hanayome', 'The Five Wedded Brides'], 'en': 'The Quintessential Quintuplets', 'ja': '五等分の花嫁'}, 'broadcast': {'day_of_the_week': 'friday', 'start_time': '01:28'}, 'status': 'finished_airing', 'start_date': '2019-01-11', 'my_list_status': {'status': 'completed', 'score': 8, 'num_episodes_watched': 12, 'is_rewatching': False, 'updated_at': '2019-09-18T14:01:57+00:00'}, 'num_episodes': 12}}, {'node': {'id': 39783, 'title': '5-toubun no Hanayome ∬', 'main_picture': {'medium': 'https://api-cdn.myanimelist.net/images/anime/1775/109514.jpg', 'large': 'https://api-cdn.myanimelist.net/images/anime/1775/109514l.jpg'}, 'alternative_titles': {'synonyms': ['Gotoubun no Hanayome 2nd Season', 'The Five Wedded Brides 2nd Season', '5-toubun no Hanayome 2nd Season', 'The Quintessential Quintuplets 2nd Season'], 'en': 'The Quintessential Quintuplets 2', 'ja': '五等分の花嫁∬'}, 'broadcast': {'day_of_the_week': 'friday', 'start_time': '01:28'}, 'status': 'currently_airing', 'start_date': '2021-01-08', 'my_list_status': {'status': 'watching', 'score': 0, 'num_episodes_watched': 3, 'is_rewatching': False, 'updated_at': '2021-01-27T17:34:26+00:00'}, 'num_episodes': 12}}]


@pytest.fixture
def list_provider():
    provider = AnimeListProvider()
    return provider


@pytest.fixture
async def list_malv1(list_provider):
    provider = list_provider
    global ANIME_API, API_VERSION
    return await provider.parse_anime_list(v1, ANIME_API='MAL', API_VERSION='V1')


@pytest.fixture
async def list_malv2b(list_provider):
    provider = list_provider
    global ANIME_API, API_VERSION
    return provider.parse_anime_list(v2b, ANIME_API='MAL', API_VERSION='V2b')


class TestAnimeInfo:
    @pytest.mark.asyncio
    async def test_malv2b_len(self, list_malv2b):
        data = list_malv2b
        assert(len(data) == 2)

    @pytest.mark.asyncio
    async def test_malv2b_list_duplicates(self, list_malv2b):
        ids = []
        for anime in list_malv2b:
            assert(anime.id not in ids)
            ids.append(anime.id)
