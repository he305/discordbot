import pytest
from discordbot.utils.streamer_utills import TwitchUtills, GoodgameUtills


class TestGoodgameApi:
    @pytest.fixture
    async def nytick_channel_id(self):
        nytick_id = await GoodgameUtills.get_channel_by_name('nytik')
        return nytick_id

    @pytest.mark.asyncio
    async def test_get_streaming_status(self, nytick_channel_id):
        id = nytick_channel_id
        status = await GoodgameUtills.get_streaming_status(id)
        assert(status is False)

    @pytest.mark.asyncio
    async def test_get_viewers(self, nytick_channel_id):
        id = nytick_channel_id
        viewers = await GoodgameUtills.get_viewers(id)
        assert(viewers == "538")

    @pytest.mark.asyncio
    async def test_get_title(self, nytick_channel_id):
        id = nytick_channel_id
        title = await GoodgameUtills.get_title(id)
        assert(title == "нытик")

    @pytest.mark.asyncio
    async def test_get_none_name(self):
        trash_id = await GoodgameUtills.get_channel_by_name('qwertyuiop')
        assert(trash_id is None)


class TestTwitchApi:
    @pytest.fixture
    async def my_channel_id(self):
        my_id = await TwitchUtills.get_channel_by_name('he305')
        return my_id

    @pytest.mark.asyncio
    async def test_get_channel_by_name(self):
        user_id = await TwitchUtills.get_channel_by_name('honeymad')
        assert(user_id == '40298003')

    @pytest.mark.asyncio
    async def test_get_streaming_status(self, my_channel_id):
        id = my_channel_id
        status = await TwitchUtills.get_streaming_status(id)
        assert(status is False)

    @pytest.mark.asyncio
    async def test_viewers(self, my_channel_id):
        id = my_channel_id
        viewers = await TwitchUtills.get_viewers(id)
        assert(viewers == '0')

    @pytest.mark.asyncio
    async def test_get_title(self, my_channel_id):
        id = my_channel_id
        title = await TwitchUtills.get_title(id)
        assert(title == "")
