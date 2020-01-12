import aiohttp
import asyncio

from hidden_data import CLIENT_ID, OAUTH_TWITCH

headers = {
    'Client-ID': CLIENT_ID,
    'Accept': 'application/vnd.twitchtv.v5+json'
}


async def get_channel_by_name(streamer_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.twitch.tv/kraken/users?login=" + streamer_name,
            timeout=10,
            headers=headers) as resp:

            stream_data = await resp.json()
            user_id = stream_data['users'][0]['_id']
            print(user_id)
            return user_id



# def get_channel_by_id(streamer_id):
#     channel = client.channels.get_by_id(streamer_id)
#     return channel


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


async def get_streaming_status(streamer_id):
    stream = await __get_stream(streamer_id)
    if stream is None:
        return False
    return True


async def get_game(streamer_id):
    stream = await __get_stream(streamer_id)
    if stream is None:
        return ""
    return stream["game"]


async def get_viewers(streamer_id):
    stream = await __get_stream(streamer_id)
    if stream is None:
        return "0"
    return stream["viewers"]


async def get_title(streamer_id):
    stream = await __get_stream(streamer_id)
    print(stream["channel"]["status"])
    if stream is None:
        return ""
    return stream["channel"]["status"]


if __name__ == "__main__":
    #print(get_title(22484632))
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(get_channel_by_name("forsen"))
    # loop.run_until_complete(get_channel_by_name("lasqa"))
    loop.run_until_complete(get_title('22484632'))
    
