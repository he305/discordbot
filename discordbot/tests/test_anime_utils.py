import pytest
from discordbot.utils.malapi import MALAPIV2b, MALAPIV1


@pytest.fixture
async def anime_list_v2b():
    anime_list = await MALAPIV2b.get_anime_list()
    return anime_list


@pytest.fixture
async def anime_list_v1():
    anime_list = await MALAPIV1.get_anime_list()
    return anime_list


class TestMalApiv2b:
    @pytest.mark.asyncio
    async def test_anime_list_len(self, anime_list_v2b, anime_list_v1):
        v2b = anime_list_v2b
        assert(len(v2b) > 200)

    @pytest.mark.asyncio
    async def test_anime_list_structure(self, anime_list_v2b):
        data = anime_list_v2b[:100]
        for d in data:
            top_level = list(d.keys())
            assert(len(top_level) == 1 and top_level[0] == "node")

    @pytest.mark.asyncio
    async def test_malv2b_search_anime(self):
        data = await MALAPIV2b.search_anime("yosuga no sora")
        assert(data[0]['node']['title'] == 'Yosuga no Sora: In Solitude, Where We Are Least Alone.')
