from flask import Flask, request, jsonify
from services.film_services import get_film_stream
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/generate-movie-url', methods=['POST'])
def generate_movie_url():
    try:
        data = request.json
        movie_title = data.get('title')

        if not movie_title:
            return jsonify({"error": "Title is required"}), 400

        result = get_film_stream(movie_title)

        if result["status"] == "error":
            return jsonify({"error": result["message"]}), 400

        combined_streams = [
            {
                "translator": result["translator1"],
                "urls": result["stream_urls1"]
            },
            {
                "translator": result["translator2"],
                "urls": result["stream_urls2"]
            }
        ]

        return jsonify({"streams": combined_streams}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
