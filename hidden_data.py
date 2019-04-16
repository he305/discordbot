import os

TOKEN = os.environ.get('TOKEN')
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
CLIENT_ID = os.environ.get('CLIENT_ID')

http_proxy  = "http://94.242.58.14:655"
https_proxy = "https://94.242.58.14:655"
ftp_proxy   = "ftp://10.10.1.10:3128"

proxyDict = { 
    "http"  : http_proxy, 
    "https" : https_proxy, 
    "ftp"   : ftp_proxy
}