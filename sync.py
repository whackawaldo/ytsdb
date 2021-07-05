import json
import requests
import pandas as pd
from tqdm import tqdm
from requests.adapters import HTTPAdapter

API_URL = "https://yts.mx/api/v2/list_movies.json"
SNAPSHOT_URL = "TODO"
KEEP_COLS = [
    "title",
    "year",
    "medium_cover_image",
    "runtime",
    "synopsis",
    "date_uploaded_unix",
]
REQUEST_SESSION = requests.Session()
REQUEST_SESSION.mount("https://", HTTPAdapter(max_retries=5))

if __name__ == "__main__":

    page = 0
    movies = {}
    pbar = tqdm()
    while True:
        page += 1

        res = REQUEST_SESSION.get(f"{API_URL}?page={page}&limit=50").json()["data"]
        if not res.get('movies'): break
        pbar.update(len(res["movies"]))

        for mov in res["movies"]:
            key = mov["imdb_code"]
            movies[key] = {col: mov.get(col) for col in KEEP_COLS}
            movies[key]["genres"] = ",".join(mov.get("genres", []))
            torrents = mov.get("torrents") or []
            for quality in ("720p", "1028p"):
                urls = [t["url"] for t in torrents if t["quality"] == quality]
                if urls: movies[key][quality] = urls[0]

    # TODO: read the latest snapshot
    # prev = requests.get(SNAPSHOT_URL).json()
    prev = {}

    # Only update if we found more movies
    if len(movies) < len(prev):
        print("Movies already up to date")
        movies = prev

    # Merge with IMDB ratings
    read_opts = dict(sep='\t', na_values=['\\N'])
    ratings = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', **read_opts)
    ratings = ratings.set_index('tconst').to_dict(orient='index')
    for key, record in movies.items():
        record.update(ratings.get(key, {}))

    # Save results to disk
    with open("output/movies.json", "w") as fh:
        json.dump(movies, fh)
