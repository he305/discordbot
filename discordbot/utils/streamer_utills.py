import aiohttp
import asyncio

from discordbot.hidden_data import CLIENT_ID

headers = {
    'Client-ID': CLIENT_ID,
    'Accept': 'application/vnd.twitchtv.v5+json'
}


class TwitchUtills:
    @staticmethod
    async def get_channel_by_name(streamer_name):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.twitch.tv/kraken/users?login=" + streamer_name,
                    timeout=10,
                    headers=headers) as resp:

                stream_data = await resp.json()
                user_id = stream_data['users'][0]['_id']
                return user_id

    @staticmethod
    async def __get_stream(streamer_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.twitch.tv/kraken/streams/" + streamer_id,
                    timeout=10,
                    headers=headers) as resp:

                stream_data = await resp.json()
                if stream_data["stream"] is None:
                    return None
                return stream_data["stream"]

    @staticmethod
    async def get_streaming_status(streamer_id):
        stream = await TwitchUtills.__get_stream(streamer_id)
        if stream is None:
            return False
        return True

    @staticmethod
    async def get_game(streamer_id):
        stream = await TwitchUtills.__get_stream(streamer_id)
        if stream is None:
            return ""
        return stream["game"]

    @staticmethod
    async def get_viewers(streamer_id):
        stream = await TwitchUtills.__get_stream(streamer_id)
        if stream is None:
            return "0"
        return stream["viewers"]

    @staticmethod
    async def get_title(streamer_id):
        stream = await TwitchUtills.__get_stream(streamer_id)
        if stream is None:
            return ""
        return stream["channel"]["status"]


class WasdUtills:
    @staticmethod
    async def __get_stream(streamer_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://wasd.tv/api/media-containers?media_container_status=RUNNING&limit=1&offset=0&media_container_type=SINGLE,COOP&channel_id=" + streamer_id,
                    timeout=10) as resp:

                stream_data = await resp.json()
                if not stream_data["result"]:
                    return None
                return stream_data["result"][0]

    @staticmethod
    async def get_streaming_status(streamer_id):
        stream = await WasdUtills.__get_stream(streamer_id)
        if stream is None:
            return False
        return True

    @staticmethod
    async def get_viewers(streamer_id):
        stream = await WasdUtills.__get_stream(streamer_id)
        if stream is None:
            return "0"
        return stream["media_container_streams"][0]["stream_current_viewers"]

    @staticmethod
    async def get_title(streamer_id):
        stream = await WasdUtills.__get_stream(streamer_id)
        if stream is None:
            return ""
        return stream["media_container_name"]


class GoodgameUtills:
    @staticmethod
    async def __get_stream(streamer_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://goodgame.ru/api/getchannelstatus?fmt=json&id=" + streamer_id,
                    timeout=10) as resp:

                stream_data = await resp.json()
                if not stream_data:
                    return None
                return stream_data[streamer_id]

    @staticmethod
    async def get_streaming_status(streamer_id):
        stream = await GoodgameUtills.__get_stream(streamer_id)
        if stream is None or stream["status"] == "Dead":
            return False
        return True

    @staticmethod
    async def get_viewers(streamer_id):
        stream = await GoodgameUtills.__get_stream(streamer_id)
        if stream is None:
            return "0"
        return stream["viewers"]

    @staticmethod
    async def get_title(streamer_id):
        stream = await GoodgameUtills.__get_stream(streamer_id)
        if stream is None:
            return ""
        return stream["title"]
