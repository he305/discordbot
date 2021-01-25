import os

TOKEN = os.environ.get('TOKEN') or None
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN") or None
OAUTH_TWITCH = os.environ.get("OAUTH_TWITCH") or None
CLIENT_ID = os.environ.get('CLIENT_ID') or None
PROXY_REQUIRED = False

USER_TORRENT = None
PASSWORD_TORRENT = None

LOGIN_MAL = None
PASS_MAL = None

ANIME_API = "MAL"
API_VERSION = "V2b"