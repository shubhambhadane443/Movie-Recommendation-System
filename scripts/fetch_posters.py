import csv
import json
import time
import requests


MOVIES_CSV = "data/movies.csv"
OUTPUT_JSON = "static/data/posters.json"
OMDB_URL = "https://www.omdbapi.com/"
OMDB_KEY = "trilogy"


def fetch_poster(title):
    try:
        resp = requests.get(
            OMDB_URL,
            params={"t": title, "apikey": OMDB_KEY},
            timeout=10
        )
        data = resp.json()
        if data.get("Response") == "True" and data.get("Poster") and data["Poster"] != "N/A":
            return data["Poster"]
    except Exception as e:
        print(f"  Error fetching '{title}': {e}")
    return None


def main():
    posters = {}
    with open(MOVIES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Fetching posters for {len(rows)} movies...")

    for i, row in enumerate(rows, 1):
        movie_id = int(row["movieId"])
        title = row["title"]
        print(f"[{i}/{len(rows)}] {title}")
        poster_url = fetch_poster(title)
        if poster_url:
            posters[str(movie_id)] = poster_url
            print(f"  [OK] {poster_url}")
        else:
            posters[str(movie_id)] = None
            print(f"  [MISS] No poster found")
        time.sleep(0.25)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(posters, f, indent=2)

    found = sum(1 for v in posters.values() if v)
    print(f"\nDone! Found {found}/{len(rows)} posters. Saved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
