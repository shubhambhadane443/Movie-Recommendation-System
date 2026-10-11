from flask import Flask, render_template, request, jsonify
from recommender import recommend_movies, movies, movie_statistics
import json
import os
import random
import requests


# ==========================================
# CREATE FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# POSTER CACHE
# ==========================================

POSTER_CACHE_PATH = os.path.join(
    os.path.dirname(__file__), "static", "data", "posters.json"
)

poster_cache = {}
if os.path.exists(POSTER_CACHE_PATH):
    with open(POSTER_CACHE_PATH, "r", encoding="utf-8") as f:
        poster_cache = json.load(f)

LINKS_PATH = os.path.join(
    os.path.dirname(__file__), "dataset", "links.csv"
)

movie_id_to_imdb = {}
if os.path.exists(LINKS_PATH):
    import csv as csv_mod
    with open(LINKS_PATH, newline="", encoding="utf-8") as f:
        reader = csv_mod.DictReader(f)
        for row in reader:
            movie_id_to_imdb[int(row["movieId"])] = row["imdbId"]

OMDB_URL = "https://www.omdbapi.com/"
OMDB_KEY = "trilogy"


def get_poster_url(movie_id):
    movie_id_str = str(movie_id)
    if movie_id_str in poster_cache and poster_cache[movie_id_str]:
        return poster_cache[movie_id_str]

    imdb_id = movie_id_to_imdb.get(movie_id)
    if imdb_id:
        url = fetch_poster_by_imdb(imdb_id)
        if url:
            poster_cache[movie_id_str] = url
            save_poster_cache()
            return url

    poster_cache[movie_id_str] = None
    return None


def fetch_poster_by_imdb(imdb_id):
    try:
        resp = requests.get(
            OMDB_URL,
            params={"i": f"tt{imdb_id}", "apikey": OMDB_KEY},
            timeout=10
        )
        data = resp.json()
        if data.get("Response") == "True" and data.get("Poster") and data["Poster"] != "N/A":
            return data["Poster"]
    except Exception:
        pass
    return None


def save_poster_cache():
    try:
        with open(POSTER_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(poster_cache, f, indent=2)
    except Exception:
        pass


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_popular_movies(limit=12):
    popular = movie_statistics.sort_values(
        by="rating_count",
        ascending=False
    ).head(limit)

    result = []
    for _, row in popular.iterrows():
        movie = movies[movies["movieId"] == row["movieId"]]
        if movie.empty:
            continue
        m = movie.iloc[0]
        result.append({
            "movieId": int(m["movieId"]),
            "title": m["title"],
            "genres": m["genres"],
            "rating": round(row["average_rating"], 1),
            "rating_count": int(row["rating_count"]),
            "poster_url": get_poster_url(int(m["movieId"]))
        })

    return result


def get_movie_details(movie_id):
    movie = movies[movies["movieId"] == movie_id]
    if movie.empty:
        return None
    m = movie.iloc[0]
    stats = movie_statistics[movie_statistics["movieId"] == movie_id]
    rating = round(stats.iloc[0]["average_rating"], 1) if not stats.empty else 0
    count = int(stats.iloc[0]["rating_count"]) if not stats.empty else 0
    return {
        "movieId": int(m["movieId"]),
        "title": m["title"],
        "genres": m["genres"],
        "rating": rating,
        "rating_count": count,
        "poster_url": get_poster_url(int(m["movieId"]))
    }


def search_movies(query, limit=10):
    query = query.lower()
    results = movies[movies["title"].str.lower().str.contains(query, na=False)]
    results = results.head(limit)
    return [
        {
            "movieId": int(row["movieId"]),
            "title": row["title"],
            "genres": row["genres"],
            "poster_url": get_poster_url(int(row["movieId"]))
        }
        for _, row in results.iterrows()
    ]


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    movie_titles = movies["title"].tolist()
    popular = get_popular_movies(12)
    return render_template(
        "index.html",
        movies=movie_titles,
        popular=popular
    )


# ==========================================
# MOVIE DETAIL PAGE
# ==========================================

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    details = get_movie_details(movie_id)
    if not details:
        return render_template("movie.html", movie=None, recommendations=[])
    recommendations = recommend_movies(details["title"], number_of_recommendations=10)
    for rec in recommendations:
        rec["poster_url"] = get_poster_url(rec["movieId"])
    return render_template(
        "movie.html",
        movie=details,
        recommendations=recommendations
    )


# ==========================================
# API: RECOMMEND
# ==========================================

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json() or {}
    movie_title = data.get("movie", "")
    number = int(data.get("number", 10))

    if not movie_title:
        return jsonify({"error": "Please select a movie."})

    recommendations = recommend_movies(movie_title, number_of_recommendations=number)

    for rec in recommendations:
        rec["poster_url"] = get_poster_url(rec["movieId"])

    return jsonify({
        "selected_movie": movie_title,
        "recommendations": recommendations
    })


# ==========================================
# API: POPULAR MOVIES
# ==========================================

@app.route("/api/popular")
def api_popular():
    limit = int(request.args.get("limit", 12))
    popular = get_popular_movies(limit)
    return jsonify({"popular": popular})


# ==========================================
# API: SEARCH MOVIES
# ==========================================

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"results": []})
    results = search_movies(query, 10)
    return jsonify({"results": results})


# ==========================================
# API: MOVIE DETAILS
# ==========================================

@app.route("/api/movie/<int:movie_id>")
def api_movie(movie_id):
    details = get_movie_details(movie_id)
    if not details:
        return jsonify({"error": "Movie not found."})
    return jsonify({"movie": details})


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(
        debug=True
    )
