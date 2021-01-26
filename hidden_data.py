import os

TOKEN = os.environ.get('TOKEN') or None
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN") or None
OAUTH_TWITCH = os.environ.get("OAUTH_TWITCH") or None
CLIENT_ID = os.environ.get('CLIENT_ID') or None
PROXY_REQUIRED = False

USER_TORRENT = None
PASSWORD_TORRENT = None

LOGIN_MAL = os.environ.get('LOGIN_MAL') or None
PASS_MAL = os.environ.get('PASS_MAL') or None

ANIME_API = os.environ.get('ANIME_API') or "MAL"
API_VERSION = os.environ.get('API_VERSION') or "V2b"
