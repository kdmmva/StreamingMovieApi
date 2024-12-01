from flask import Flask, request, jsonify
from services.film_services import get_html_url,compare_descriptions,get_film_stream,get_serial_stream
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/generate-movie-url', methods=['POST'])
def generate_movie_url():
    try:
        data = request.json
        movie_title = data.get('title')
        client_description = data.get('description')

        if not movie_title or not client_description:
            return jsonify({"error": "Title and description are required"}), 400

        rezka_result = get_html_url(movie_title)
        if not rezka_result:
            return jsonify({"error": "Could not find the movie on Rezka"}), 404

        rezka_description = rezka_result['description']
        similarity = compare_descriptions(client_description, rezka_description)

        # if similarity < 0.5:
        #     return jsonify({"error": "Description does not match"}), 400

        if rezka_result['type'] == 'Movie':
            stream_result = get_film_stream(movie_title)

        elif rezka_result['type'] == 'Serial':
            stream_result = get_serial_stream(movie_title)
        else:
            return jsonify({"error": "Unknown type returned from Rezka"}), 400

        if stream_result.get('status') == 'error':
            return jsonify({"error": stream_result.get('message')}), 400

        return jsonify({
            "type": rezka_result['type'],
            "similarity": similarity,
            "streams": stream_result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
