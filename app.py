import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Check if API key exists
if not TMDB_API_KEY:
    raise ValueError(
        "TMDB_API_KEY not found! Create a .env file with:\nTMDB_API_KEY=YOUR_API_KEY"
    )

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
})


def filter_movies(movies):
    return [m for m in movies if m.get("poster_path") and m.get("title")]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/popular")
def get_popular():
    try:
        response = session.get(
            f"{BASE_URL}/trending/movie/day",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return jsonify(filter_movies(results)[:20])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search")
def search_movies():
    query = request.args.get("query", "")

    if not query:
        return jsonify([])

    try:
        response = session.get(
            f"{BASE_URL}/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": query,
                "language": "en-US",
                "include_adult": "false"
            },
            timeout=10
        )

        response.raise_for_status()
        results = response.json().get("results", [])

        return jsonify(filter_movies(results))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/movie/<int:movie_id>/credits")
def get_credits(movie_id):
    try:
        response = session.get(
            f"{BASE_URL}/movie/{movie_id}/credits",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )

        response.raise_for_status()

        cast = [
            member["name"]
            for member in response.json().get("cast", [])[:12]
        ]

        return jsonify(cast)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recommendations/<int:movie_id>")
def get_recommendations(movie_id):
    try:
        movie_info = session.get(
            f"{BASE_URL}/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )

        movie_info.raise_for_status()
        movie_info = movie_info.json()

        original_language = movie_info.get("original_language", "en")

        recommendations = session.get(
            f"{BASE_URL}/movie/{movie_id}/recommendations",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )

        recommendations.raise_for_status()
        recommendations = recommendations.json().get("results", [])

        discover = session.get(
            f"{BASE_URL}/discover/movie",
            params={
                "api_key": TMDB_API_KEY,
                "with_original_language": original_language,
                "sort_by": "popularity.desc"
            },
            timeout=10
        )

        discover.raise_for_status()
        discover = discover.json().get("results", [])

        combined = (
            [
                movie
                for movie in recommendations
                if movie.get("original_language") == original_language
            ]
            + discover
        )

        seen = {movie_id}
        final_movies = []

        for movie in combined:
            if movie["id"] not in seen:
                final_movies.append(movie)
                seen.add(movie["id"])

        for movie in recommendations:
            if movie["id"] not in seen:
                final_movies.append(movie)
                seen.add(movie["id"])

        return jsonify(filter_movies(final_movies)[:20])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)