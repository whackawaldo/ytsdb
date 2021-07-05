import json
import requests
from tqdm import tqdm

API_URL = "https://yts.mx/api/v2/list_movies.json"
SNAPSHOT_URL = "TODO"
KEEP_COLS = [
    "title",
    "year",
    "medium_cover_image",
    "rating",
    "runtime",
    "synopsis",
    "date_uploaded_unix",
]

if __name__ == "__main__":

    page = 0
    movies = {}
    pbar = tqdm()
    while True:
        pbar.update()
        page += 1

        res = requests.get(f"{API_URL}?page={page}&limit=50").json()["data"]
        if not res.get('movies'): break
        for mov in res["movies"]:
            key = mov["imdb_code"]
            movies[key] = {col: mov.get(col) for col in KEEP_COLS}
            movies["genres"] = ",".join(mov.get("genres", []))
            torrents = mov.get("torrents") or []
            for quality in ("720p", "1028p"):
                urls = [t["url"] for t in torrents if t["quality"] == quality]
                if urls: movies[key][quality] = urls[0]

    # TODO: read the latest snapshot
    # prev = requests.get(SNAPSHOT_URL).json()
    prev = {}

    # If we found more movies, update snapshot
    with open("output/movies.json", "w") as fh:
        if len(movies) > len(prev):
            json.dump(movies, fh)
        else:
            json.dump(prev, fh)
