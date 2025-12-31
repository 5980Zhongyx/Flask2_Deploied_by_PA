#!/usr/bin/env python3
import urllib.request

url = "https://5980Zhongyx.pythonanywhere.com/films"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        html = r.read().decode("utf-8", errors="ignore")
        count = html.count("/static/posters/")
        print("LEN_HTML:", len(html))
        print("POSTER_TAG_COUNT:", count)
        # print first 800 chars
        print(html[:800])
except Exception as e:
    print("ERROR:", e)
