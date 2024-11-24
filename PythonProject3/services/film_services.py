import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from HdRezkaApi import *
import json

def get_film_url(film_name):
    query = quote_plus(film_name)
    search_url = f'https://rezka.ag/search/?do=search&subaction=search&q={query}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    film_item = soup.find('div', class_='b-content__inline_item')

    if film_item:
        film_url = film_item.find('a')['href']

        film_response = requests.get(film_url, headers=headers)
        if film_response.status_code == 200:
            return film_url
        else:
            print(f"Film is not accessible. Status code: {film_response.status_code}")
            return None
    else:
        print("Film not found.")
        return None


def get_film_stream(film_name):
    try:
        url = get_film_url(film_name)
        if not url:
            return {"status": "error", "message": "URL not found"}

        rezka = HdRezkaApi(url)

        qualities = ["360p", "480p", "720p", "1080p", "1080p Ultra"]
        stream_urls = {}

        for quality in qualities:
            stream_url = rezka.getStream()(quality)
            if stream_url:
                stream_urls[quality] = stream_url

        if len(stream_urls) < len(qualities):
            missing_qualities = set(qualities) - set(stream_urls.keys())
            return {
                "status": "error",
                "message": f"Not all qualities available. Missing: {', '.join(missing_qualities)}",
            }

        return {"status": "success", "stream_urls": stream_urls}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# film_name = "The Substance"
# urls = get_film_stream(film_name)
# print(urls)