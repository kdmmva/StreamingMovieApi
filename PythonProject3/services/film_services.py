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
        # Получаем URL объекта
        result = get_html_url(serial_name)
        if not result or 'url' not in result:
            return {"status": "error", "message": "URL not found"}

        url = result['url']

        # Создаем объект API на основе URL
        rezka = HdRezkaApi(url)

        available_translators = rezka.translators

        # Выбираем переводчик
        translator_name = "Оригинал (+субтитры)"  # Можно заменить на индекс или другой переводчик
        if translator_name not in available_translators:
            return {"status": "error", "message": f"Translator '{translator_name}' not found"}

        all_season_streams = {}

        # Перебираем сезоны
        season_number = 1
        while True:
            try:
                print(f"Processing season {season_number}...")

                # Получаем потоки для текущего сезона
                season_streams_generator = rezka.getSeasonStreams(
                    season=season_number,
                    translation=translator_name,
                    ignore=True,
                    progress=lambda current, total: print(f"Season {season_number} progress: {current}/{total}")
                )

                # Преобразуем генератор в словарь
                season_streams = dict(season_streams_generator)

                if not season_streams:
                    print(f"No streams found for season {season_number}. Stopping.")
                    break

                # Преобразуем данные потоков в удобный формат
                all_season_streams[season_number] = {
                    episode: {
                        quality: stream(quality)
                        for quality in ["360p", "480p", "720p", "1080p", "1080p Ultra"]
                        if callable(stream)
                    }
                    for episode, stream in season_streams.items()
                }

                season_number += 1

            except Exception as e:
                print(f"Error processing season {season_number}: {e}")
                break

        if not all_season_streams:
            return {"status": "error", "message": "No streams available"}

        return {
            "status": "success",
            "type": "Serial",
            "translator": translator_name,
            "streams": all_season_streams
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}



# serial_name = "Sans famille / An Orphan's Tale"

result = get_serial_stream("Game of Thrones")

print(result)
# film_name = "The Substance"
# urls = get_film_stream(film_name)
# print(urls)

result = get_html_url("Sans famille / An Orphan's Tale")
print(result)