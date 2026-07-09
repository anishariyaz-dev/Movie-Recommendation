import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
TMDB_API_KEY = "50044de0d0150536a512d4041d488073"
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
        response = session.get(f"{BASE_URL}/trending/movie/day", params={"api_key": TMDB_API_KEY})
        results = response.json().get('results', [])
        return jsonify(filter_movies(results)[:20])
    except Exception as e:
        return jsonify([]), 500

@app.route('/search')
def search_movies():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    try:
        params = {"api_key": TMDB_API_KEY, "query": query, "language": "en-US", "include_adult": "false"}
        response = session.get(f"{BASE_URL}/search/movie", params=params, timeout=5)
        return jsonify(filter_movies(response.json().get('results', [])))
    except Exception as e:
        return jsonify([]), 500

@app.route('/movie/<int:movie_id>/credits')
def get_credits(movie_id):
    try:
        response = session.get(f"{BASE_URL}/movie/{movie_id}/credits", params={"api_key": TMDB_API_KEY})
        cast = [member['name'] for member in response.json().get('cast', [])[:12]]
        return jsonify(cast)
    except Exception as e:
        return jsonify([]), 500

@app.route('/recommendations/<int:movie_id>')
def get_recommendations(movie_id):
    try:
        movie_info = session.get(f"{BASE_URL}/movie/{movie_id}", params={"api_key": TMDB_API_KEY}).json()
        orig_lang = movie_info.get('original_language', 'en')
        
        rec_res = session.get(f"{BASE_URL}/movie/{movie_id}/recommendations", params={"api_key": TMDB_API_KEY})
        recs = rec_res.json().get('results', [])

        discover_params = {"api_key": TMDB_API_KEY, "with_original_language": orig_lang, "sort_by": "popularity.desc"}
        disc_res = session.get(f"{BASE_URL}/discover/movie", params=discover_params)
        discovery = disc_res.json().get('results', [])

        combined = [m for m in recs if m.get('original_language') == orig_lang] + discovery
        seen_ids = {movie_id}; final_list = []
        for m in combined:
            if m['id'] not in seen_ids:
                final_list.append(m); seen_ids.add(m['id'])
        for m in recs:
            if m['id'] not in seen_ids:
                final_list.append(m); seen_ids.add(m['id'])

        return jsonify(filter_movies(final_list)[:20])
    except Exception as e:
        return jsonify([]), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)