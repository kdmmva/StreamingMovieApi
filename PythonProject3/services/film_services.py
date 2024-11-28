import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from HdRezkaApi import *
import json

def get_html_url(object_name):
    query = quote_plus(object_name)
    search_url = f'https://rezka.ag/search/?do=search&subaction=search&q={query}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    object_item = soup.find('div', class_='b-content__inline_item')

    if object_item:
        obj_url = object_item.find('a')['href']

        object_response = requests.get(obj_url, headers=headers)
        if object_response.status_code == 200:
            object_soup = BeautifulSoup(object_response.text, 'html.parser')

            is_serial = False

            season_info = object_soup.find('div', class_='b-simple_episodes__title')
            if season_info and 'сезон' in season_info.get_text(strip=True).lower():
                is_serial = True

            episodes_list = object_soup.find('div', class_='b-simple_episodes__list')
            if episodes_list:
                is_serial = True

            duration_info = object_soup.find('div', class_='b-post__info')
            if duration_info:
                duration_text = duration_info.get_text(strip=True).lower()
                if 'мин' in duration_text and 'серий' in duration_text:
                    is_serial = True

            additional_info = object_soup.get_text(strip=True).lower()
            if 'эпизод' in additional_info or 'серия' in additional_info:
                is_serial = True

            obj_type = 'Serial' if is_serial else 'Movie'
            return {
                'url': obj_url,
                'type': obj_type
            }
        else:
            print(f"Object page is not accessible. Status code: {object_response.status_code}")
            return None
    else:
        print("Object not found on the search page.")
        return None

def get_film_stream(film_name):
    try:
        url = get_html_url(film_name)
        if not url:
            return {"status": "error", "message": "URL not found"}

        rezka = HdRezkaApi(url)

        available_translators = rezka.translators
        if "Дубляж" not in available_translators:
            return {"status": "error", "message": "Translator 'Дубляж' not found"}

        current_translator1 = "Дубляж"

        qualities = ["360p", "480p", "720p", "1080p", "1080p Ultra"]
        stream_urls1 = {}

        for quality in qualities:
            try:
                stream_url = rezka.getStream(translation=current_translator1)(quality)
                if stream_url:
                    stream_urls1[quality] = stream_url
            except Exception as e:
                print(f"Error fetching quality {quality}: {e}")
                continue

        if not stream_urls1:
            return {"status": "error", "message": "No streams available"}

        if "Оригинал (+субтитры)" not in available_translators:
            return {"status": "error", "message": "Translator 'Оригинал (+субтитры)' not found"}

        current_translator2 = "Оригинал (+субтитры)"
        stream_urls2 = {}

        for quality in qualities:
            try:
                stream_url = rezka.getStream(translation=current_translator2)(quality)
                if stream_url:
                    stream_urls2[quality] = stream_url
            except Exception as e:
                print(f"Error fetching quality {quality}: {e}")
                continue

        if not stream_urls2:
            return {"status": "error", "message": "No streams available"}

        return {
            "status": "success",
            "stream_urls1": stream_urls1,
            "translator1": current_translator1,
            "stream_urls2": stream_urls2,
            "translator2": current_translator2
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_serial_stream(serial_name):
    try:
        url = get_html_url(serial_name)
        if not url:
            return {"status": "error", "message": "URL not found"}

        rezka = HdRezkaApi(url)

        available_translators = rezka.translators
        if not isinstance(available_translators, list):
            print(f"Unexpected type for translators: {type(available_translators)}")
            return {"status": "error", "message": "Invalid translators format"}

        if "Дубляж" not in available_translators:
            return {"status": "error", "message": "Translator 'Дубляж' not found"}

        current_translator = "Дубляж"

        qualities = ["360p", "480p", "720p", "1080p", "1080p Ultra"]
        all_stream_urls = {}

        seasons = rezka.seasons
        if not isinstance(seasons, list):
            print(f"Unexpected type for seasons: {type(seasons)}")
            return {"status": "error", "message": "Invalid seasons format"}

        if not seasons:
            return {"status": "error", "message": "No seasons found"}

        for season in seasons:
            all_stream_urls[season] = {}
            episodes = rezka.getEpisodes(season)

            if not isinstance(episodes, list):
                print(f"Unexpected type for episodes: {type(episodes)}")
                continue

            if not episodes:
                print(f"No episodes found for season {season}")
                continue

            for episode in episodes:
                all_stream_urls[season][episode] = {}
                for quality in qualities:
                    try:
                        stream_function = rezka.getStream(
                            translation=current_translator,
                            season=season,
                            episode=episode
                        )

                        if not callable(stream_function):
                            print(f"Unexpected type for stream_function: {type(stream_function)}")
                            continue

                        stream_url = stream_function(quality)

                        if not isinstance(stream_url, str):
                            print(f"Unexpected type for stream_url: {type(stream_url)}")
                            continue

                        all_stream_urls[season][episode][quality] = stream_url
                    except Exception as e:
                        print(f"Error fetching S{season}E{episode} quality {quality}: {e}")
                        continue

        if not all_stream_urls:
            return {"status": "error", "message": "No streams available"}

        return {
            "status": "success",
            "translator": current_translator,
            "streams": all_stream_urls
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


serial_name = "Культ"

result = get_serial_stream("serial_name")
if result["status"] == "success":
    for season, episodes in result["streams"].items():
        print(f"Season {season}:")
        for episode, qualities in episodes.items():
            print(f"  Episode {episode}:")
            for quality, url in qualities.items():
                print(f"    {quality}: {url}")
else:
    print(f"Error: {result['message']}")

# film_name = "The Substance"
# urls = get_film_stream(film_name)
# print(urls)

# result = get_html_url("Sans famille / An Orphan's Tale")
# print(result)