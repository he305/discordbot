from twitch import TwitchClient
from twitch.constants import STREAM_TYPE_ALL

from hidden_data import CLIENT_ID, OAUTH_TWITCH

client = TwitchClient(client_id=CLIENT_ID, oauth_token=OAUTH_TWITCH)


def get_channel_by_name(streamer_name):
    channels = client.users.translate_usernames_to_ids(streamer_name)
    return channels[0].id


def get_channel_by_id(streamer_id):
    channel = client.channels.get_by_id(streamer_id)
    return channel


def __get_stream(streamer_id):
    stream = client.streams.get_stream_by_user(channel_id=streamer_id, stream_type=STREAM_TYPE_ALL)
    if stream is None:
        return None
    return stream


def get_streaming_status(streamer_id):
    stream = __get_stream(streamer_id)
    if stream is None:
        return False
    return True


def get_game(streamer_id):
    stream = __get_stream(streamer_id)
    if stream is None:
        return ""
    return stream["game"]


def get_viewers(streamer_id):
    stream = __get_stream(streamer_id)
    if stream is None:
        return "0"
    return stream["viewers"]


def get_title(streamer_id):
    stream = __get_stream(streamer_id)
    if stream is None:
        return ""
    return stream["channel"]["status"]


if __name__ == "__main__":
    print(get_title(22484632))
    print(get_channel_by_name("lasqa"))
