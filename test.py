url = 'https://www.youtube.com/playlist?list=PL85D130CFB0231675'

if 'list=' in url:
    new_url = 'https://www.youtube.com/playlist?' + url[url.rfind('list'):]

print(new_url)