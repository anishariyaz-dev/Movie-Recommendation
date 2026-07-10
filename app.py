import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
})

def filter_movies(movies):
    return [m for m in movies if m.get('poster_path') and m.get('title')]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/popular')
def get_popular():
    try:
        response = session.get(
            f"{BASE_URL}/trending/movie/day",
            params={"api_key": TMDB_API_KEY},
            timeout=5
        )
        response.raise_for_status()
        results = response.json().get('results', [])
        return jsonify(filter_movies(results)[:20])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search')
def search_movies():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    try:
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "language": "en-US",
            "include_adult": "false"
        }

        response = session.get(
            f"{BASE_URL}/search/movie",
            params=params,
            timeout=5
        )
        response.raise_for_status()

        return jsonify(filter_movies(response.json().get('results', [])))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/movie/<int:movie_id>/credits')
def get_credits(movie_id):
    try:
        response = session.get(
            f"{BASE_URL}/movie/{movie_id}/credits",
            params={"api_key": TMDB_API_KEY},
            timeout=5
        )
        response.raise_for_status()

        cast = [
            member['name']
            for member in response.json().get('cast', [])[:12]
        ]

        return jsonify(cast)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations/<int:movie_id>')
def get_recommendations(movie_id):
    try:
        movie_info = session.get(
            f"{BASE_URL}/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY},
            timeout=5
        )
        movie_info.raise_for_status()
        movie_info = movie_info.json()

        orig_lang = movie_info.get('original_language', 'en')

        rec_res = session.get(
            f"{BASE_URL}/movie/{movie_id}/recommendations",
            params={"api_key": TMDB_API_KEY},
            timeout=5
        )
        rec_res.raise_for_status()
        recs = rec_res.json().get('results', [])

        discover_params = {
            "api_key": TMDB_API_KEY,
            "with_original_language": orig_lang,
            "sort_by": "popularity.desc"
        }

        disc_res = session.get(
            f"{BASE_URL}/discover/movie",
            params=discover_params,
            timeout=5
        )
        disc_res.raise_for_status()
        discovery = disc_res.json().get('results', [])

        combined = [
            m for m in recs
            if m.get('original_language') == orig_lang
        ] + discovery

        seen_ids = {movie_id}
        final_list = []

        for movie in combined:
            if movie['id'] not in seen_ids:
                final_list.append(movie)
                seen_ids.add(movie['id'])

        for movie in recs:
            if movie['id'] not in seen_ids:
                final_list.append(movie)
                seen_ids.add(movie['id'])

        return jsonify(filter_movies(final_list)[:20])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)