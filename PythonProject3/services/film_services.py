import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from HdRezkaApi import *
from deep_translator import GoogleTranslator
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

            description_tag = object_soup.find('div', class_='b-post__description_text')
            rezka_description = description_tag.get_text(strip=True) if description_tag else ""

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
                'type': obj_type,
                'description': rezka_description
            }
        else:
            print(f"Object page is not accessible. Status code: {object_response.status_code}")
            return None
    else:
        print("Object not found on the search page.")
        return None

# def compare_descriptions(client_description, rezka_description):
#     similarity = SequenceMatcher(None, translated_client_description, rezka_description).ratio()
#     return similarity

def compare_descriptions(client_desc, rezka_desc):
    translated_client_description = GoogleTranslator(source="auto", target="ru").translate(client_desc)

    vectorizer = TfidfVectorizer().fit_transform([translated_client_description, rezka_desc])
    vectors = vectorizer.toarray()

    similarity_matrix = cosine_similarity(vectors)

    return similarity_matrix[0, 1]

def get_film_stream(film_name):
    try:
        result = get_html_url(film_name)
        if not result or 'url' not in result:
            return {"status": "error", "message": "URL not found"}

        url = result['url']
        rezka = HdRezkaApi(url)

        available_translators = rezka.translators

        custom_translators = [
            "Дубляж",
            "Оригинал (+субтитры)",
            "Авторский перевод"
        ]

        matching_translators = [t for t in custom_translators if t in available_translators]

        if not matching_translators:
            print("No preferred translators found. Proceeding without specifying a translator.")
            matching_translators = [None]

        qualities = ["360p", "480p", "720p", "1080p", "1080p Ultra"]

        streams_by_translator = {}

        for translator_name in matching_translators:
            print(f"Processing translator: {translator_name if translator_name else 'No translator specified'}")
            stream_urls = {}
            subtitles_info = {}

            for quality in qualities:
                try:
                    stream = rezka.getStream(translation=translator_name) if translator_name else rezka.getStream()
                    video_url = stream(quality) if callable(stream) else None

                    if video_url:
                        stream_urls[quality] = video_url

                        if translator_name == "Оригинал (+субтитры)" and hasattr(stream, "subtitles") and stream.subtitles:
                            subtitles = stream.subtitles
                            subtitles_info = {
                                "keys": subtitles.keys,
                                "subtitles": subtitles.subtitles,
                            }
                except Exception as e:
                    print(f"Error fetching quality {quality}: {e}")
                    continue

            if stream_urls:
                streams_by_translator[translator_name if translator_name else "No translator"] = {
                    "streams": stream_urls,
                    "subtitles": subtitles_info if translator_name == "Оригинал (+субтитры)" else None
                }

        if not streams_by_translator:
            return {"status": "error", "message": "No streams available for any translator"}

        return {
            "status": "success",
            "streams_by_translator": streams_by_translator
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_serial_stream(serial_name):
    try:
        result = get_html_url(serial_name)
        if not result or 'url' not in result:
            return {"status": "error", "message": "URL not found"}

        url = result['url']
        rezka = HdRezkaApi(url)

        available_translators = rezka.translators

        custom_translators = [
            "Дубляж",
            "Оригинал (+субтитры)",
            "лостфильм (LostFilm)"
        ]

        matching_translators = [t for t in custom_translators if t in available_translators]

        if not matching_translators:
            print("No preferred translators found. Proceeding without specifying a translator.")
            translator_name = None
        else:
            translator_name = matching_translators[0]
            print(f"Using translator: {translator_name}")

        all_season_streams = {}

        season_number = 1
        while True:
            try:
                print(f"Processing season {season_number}...")

                season_streams_generator = rezka.getSeasonStreams(
                    season=season_number,
                    translation=translator_name,
                    ignore=True,
                    progress=lambda current, total: print(f"Season {season_number} progress: {current}/{total}")
                ) if translator_name else rezka.getSeasonStreams(
                    season=season_number,
                    ignore=True,
                    progress=lambda current, total: print(f"Season {season_number} progress: {current}/{total}")
                )

                season_streams = dict(season_streams_generator)

                if not season_streams:
                    print(f"No streams found for season {season_number}. Stopping.")
                    break

                all_season_streams[season_number] = {
                    episode: {
                        "streams": {
                            quality: stream(quality)
                            for quality in ["360p", "480p", "720p", "1080p", "1080p Ultra"]
                            if callable(stream)
                        },
                        "subtitles": (
                            {
                                "keys": stream.subtitles.keys,
                                "subtitles": stream.subtitles.subtitles
                            }
                            if translator_name == "Оригинал (+субтитры)" and hasattr(stream, "subtitles") and stream.subtitles
                            else None
                        )
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
            "translator": translator_name if translator_name else "No translator specified",
            "streams": all_season_streams
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# serial_name = "Game of Thrones"
#
# result = get_serial_stream(serial_name)

# print(result)

# film_name = "The Substance"
# urls = get_film_stream(film_name)
# print(urls)

# result = get_html_url("Sans famille / An Orphan's Tale")
# print(result)

# film_name = "The Shawshank Redemption"
# result = get_film_stream(film_name)