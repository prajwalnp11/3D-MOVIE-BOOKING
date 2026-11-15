import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie

class Command(BaseCommand):
    help = 'Fetches real movie posters, backdrops, and trailer URLs from TMDB API'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, help='Sync a specific movie title')

    def handle(self, *args, **options):
        api_key = getattr(settings, 'TMDB_API_KEY', None)
        if not api_key:
            self.stderr.write(self.style.ERROR('TMDB_API_KEY not configured in settings or .env'))
            return

        title_arg = options.get('title')
        if title_arg:
            movies = Movie.objects.filter(title__icontains=title_arg)
        else:
            movies = Movie.objects.all()

        base_url = 'https://api.themoviedb.org/3'
        self.stdout.write(f"Syncing {movies.count()} movies with TMDB API...")

        for movie in movies:
            tmdb_id = movie.tmdb_id
            
            # If tmdb_id is missing or placeholder (>100000 and <200000), search TMDB by title
            if not tmdb_id or (100000 <= tmdb_id <= 100010):
                search_res = requests.get(
                    f"{base_url}/search/movie",
                    params={'api_key': api_key, 'query': movie.title.split(':')[0]}
                )
                if search_res.status_code == 200:
                    results = search_res.json().get('results', [])
                    if results:
                        tmdb_id = results[0]['id']
                        movie.tmdb_id = tmdb_id

            if not tmdb_id:
                self.stdout.write(self.style.WARNING(f"Skipping {movie.title} (No TMDB ID found)"))
                continue

            # Fetch movie details
            res = requests.get(f"{base_url}/movie/{tmdb_id}", params={'api_key': api_key})
            if res.status_code != 200:
                self.stdout.write(self.style.WARNING(f"Could not fetch details for {movie.title} (ID: {tmdb_id})"))
                continue

            data = res.json()
            poster_path = data.get('poster_path')
            backdrop_path = data.get('backdrop_path')

            if poster_path:
                movie.poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            if backdrop_path:
                movie.backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"

            # Fetch multi-language videos for Indian & international trailers
            vid_res = requests.get(
                f"{base_url}/movie/{tmdb_id}/videos",
                params={'api_key': api_key, 'include_video_language': 'en,ta,te,hi,ml,null'}
            )
            if vid_res.status_code == 200:
                vids = vid_res.json().get('results', [])
                trailers = [v for v in vids if v.get('site') == 'YouTube' and v.get('type') == 'Trailer']
                if not trailers:
                    trailers = [v for v in vids if v.get('site') == 'YouTube']
                if trailers:
                    movie.trailer_url = f"https://www.youtube.com/watch?v={trailers[0]['key']}"

            # Fetch Cast & Crew
            cred_res = requests.get(f"{base_url}/movie/{tmdb_id}/credits", params={'api_key': api_key})
            if cred_res.status_code == 200:
                cdata = cred_res.json()
                cast_names = [c['name'] for c in cdata.get('cast', [])[:6]]
                directors = [c['name'] for c in cdata.get('crew', []) if c.get('job') == 'Director']
                if cast_names:
                    movie.cast = ', '.join(cast_names)
                if directors:
                    movie.crew = directors[0]

            movie.save()
            self.stdout.write(self.style.SUCCESS(f"✔ {movie.title} -> Poster: {movie.poster_url}"))

        self.stdout.write(self.style.SUCCESS("TMDB Sync complete!"))
