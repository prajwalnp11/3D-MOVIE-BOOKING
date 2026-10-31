
import requests
from django.conf import settings
from django.utils.dateparse import parse_date
from movies.models import Movie

BASE_URL = "https://api.themoviedb.org/3"


def fetch_popular_movies():
    url = f"{BASE_URL}/movie/popular"

    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    movies = response.json()["results"]

    for item in movies:
        poster_path = item.get("poster_path")

        poster_url = (
            f"https://image.tmdb.org/t/p/w500{poster_path}"
            if poster_path else ""
        )

        Movie.objects.update_or_create(
            tmdb_id=item["id"],
            defaults={
                "title": item["title"],
                "description": item.get("overview", ""),
                "poster_url": poster_url,
                "release_date": parse_date(
                    item.get("release_date", "")
                ),
                "rating": item.get("vote_average", 0),
            }
        )

    return len(movies)


def fetch_movie_trailer(tmdb_id):
    url = f"{BASE_URL}/movie/{tmdb_id}/videos"

    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    videos = response.json().get("results", [])

    # Prefer an official YouTube trailer
    for video in videos:
        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
        ):
            return f"https://www.youtube.com/embed/{video['key']}"

    # Otherwise use any YouTube trailer
    for video in videos:
        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
        ):
            return f"https://www.youtube.com/embed/{video['key']}"

    return ""

def fetch_movie_trailer(movie):
    url = f"{BASE_URL}/movie/{movie.tmdb_id}/videos"

    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    videos = response.json().get("results", [])

    trailers = [
        video for video in videos
        if video.get("site") == "YouTube"
        and video.get("type") == "Trailer"
    ]

    if not trailers:
        trailers = [
            video for video in videos
            if video.get("site") == "YouTube"
            and video.get("type") == "Teaser"
        ]

    if not trailers:
        return None

    official = [video for video in trailers if video.get("official")]

    selected = (official or trailers)[0]

    movie.trailer_url = (
        f"https://www.youtube.com/watch?v={selected['key']}"
    )

    movie.save(update_fields=["trailer_url"])

    return movie.trailer_url
