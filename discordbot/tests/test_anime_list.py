import pytest
from discordbot.anime.anime_list import AnimeListProvider


@pytest.fixture
def list_provider():
    provider = AnimeListProvider()
    return provider


@pytest.fixture
async def list_malv1(list_provider):
    provider = list_provider
    global ANIME_API, API_VERSION
    return await provider.get_anime_list(ANIME_API='MAL', API_VERSION='V1')


@pytest.fixture
async def list_malv2b(list_provider):
    provider = list_provider
    global ANIME_API, API_VERSION
    return await provider.get_anime_list(ANIME_API='MAL', API_VERSION='V2b')


class TestAnimeInfo:
    @pytest.mark.asyncio
    async def test_malv2b_len(self, list_malv2b):
        data = list_malv2b
        assert(len(data) > 200)

    @pytest.mark.asyncio
    async def test_malv2b_list_duplicates(self, list_malv2b):
        ids = []
        for anime in list_malv2b:
            assert(anime.id not in ids)
            ids.append(anime.id)
