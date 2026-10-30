
from django.shortcuts import render, get_object_or_404

from .models import Movie
from .services.tmdb import fetch_movie_trailer


def home(request):
    movies = Movie.objects.all().order_by('-rating')
    featured_movie = movies.first()

    return render(request, 'movies/home.html', {
        'movies': movies,
        'featured_movie': featured_movie,
    })


def movie_detail(request, tmdb_id):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    trailer_url = movie.trailer_url

    if not trailer_url:
        try:
            trailer_url = fetch_movie_trailer(movie.tmdb_id)

            if trailer_url:
                movie.trailer_url = trailer_url
                movie.save(update_fields=['trailer_url'])

        except Exception as error:
            print("Trailer fetching failed:", error)

    return render(request, 'movies/detail.html', {
        'movie': movie,
        'trailer_url': trailer_url,
    })
