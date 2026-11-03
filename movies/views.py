from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import date, timedelta
from .models import Movie, Genre
from cinemas.models import Cinema, Show
from theatres.models import Theatre, Showtime
from bookings.models import Snack


def home(request):
    city = request.GET.get('city') or request.session.get('selected_city') or 'Kochi'
    request.session['selected_city'] = city

    # 1. Featured & Trending Movies
    all_movies = Movie.objects.all().order_by('-rating')
    featured_movies = Movie.objects.filter(is_featured=True).order_by('-rating')[:5]
    if not featured_movies.exists():
        featured_movies = all_movies[:5]

    trending_movies = Movie.objects.filter(is_trending=True).order_by('-rating')[:8]
    now_showing_movies = Movie.objects.filter(status='NOW_SHOWING').order_by('-rating')[:8]
    if not now_showing_movies.exists():
        now_showing_movies = all_movies[:8]

    upcoming_movies = Movie.objects.filter(status='UPCOMING').order_by('-release_date')[:8]
    if not upcoming_movies.exists():
        upcoming_movies = all_movies[8:16]

    # 2. Popular Cinemas in selected city
    popular_cinemas = Cinema.objects.filter(city__iexact=city).order_by('-rating')[:4]
    if not popular_cinemas.exists():
        popular_cinemas = Cinema.objects.all().order_by('-rating')[:4]

    # 3. Special Events
    special_events = [
        {
            'title': 'Christopher Nolan 70mm IMAX Retro',
            'category': 'SPECIAL SCREENING',
            'badge': 'EXCLUSIVE',
            'date_info': 'Nov 14 - 18, 2026',
            'venue': 'PVR ICON: Lulu Mall, Kochi',
            'image_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80',
            'description': 'Witness The Dark Knight, Interstellar, and Oppenheimer in original 70mm dual-laser IMAX format.'
        },
        {
            'title': 'CineVerse Esports Arena Finals 2026',
            'category': 'LIVE ESPORTS',
            'badge': 'STADIUM ATMOS',
            'date_info': 'Nov 22, 2026 • 6:00 PM',
            'venue': 'PVR IMAX: Vega City, Bengaluru',
            'image_url': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80',
            'description': 'Live grand finals projected onto the giant IMAX screen with 12-channel surround sound.'
        },
        {
            'title': 'Studio Ghibli & Anime Film Gala',
            'category': 'FESTIVAL',
            'badge': 'JAPANESE / ENG',
            'date_info': 'Dec 02 - 06, 2026',
            'venue': 'PVR INOX: Jio World Drive, Mumbai',
            'image_url': 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=800&q=80',
            'description': 'A week of restored classics with themed gourmet matcha treats and collector souvenir passes.'
        },
    ]

    # 4. Horizontal Date Bar
    today = date.today()
    date_options = []
    for i in range(5):
        d = today + timedelta(days=i)
        date_options.append({
            'date_str': d.strftime('%Y-%m-%d'),
            'day_name': 'Today' if i == 0 else ('Tomorrow' if i == 1 else d.strftime('%a')),
            'day_num': d.strftime('%d'),
            'month': d.strftime('%b'),
            'is_selected': i == 0
        })

    # Cinemas with shows for quick showtimes section
    cinemas_with_shows = []
    for c in popular_cinemas:
        today_shows = list(Show.objects.filter(cinema=c, show_date=today).select_related('movie', 'screen').order_by('show_time')[:5])
        cinemas_with_shows.append({
            'cinema': c,
            'shows': today_shows
        })

    genres = Genre.objects.all()[:8]
    languages = ['English', 'Malayalam', 'Hindi', 'Tamil']
    snacks = Snack.objects.all().order_by('category', 'price')[:4]

    return render(request, 'movies/home.html', {
        'featured_movies': featured_movies,
        'trending_movies': trending_movies,
        'now_showing_movies': now_showing_movies,
        'upcoming_movies': upcoming_movies,
        'popular_cinemas': popular_cinemas,
        'cinemas_with_shows': cinemas_with_shows,
        'special_events': special_events,
        'date_options': date_options,
        'genres': genres,
        'languages': languages,
        'city': city,
        'snacks': snacks,
    })


def movie_list(request):
    """
    Dedicated Movie Listing Page with search, genre, language, and status filtering.
    """
    genre_slug = request.GET.get('genre')
    language = request.GET.get('language')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('q', '').strip()

    movies = Movie.objects.all().order_by('-rating')

    if genre_slug and genre_slug.lower() != 'all':
        movies = movies.filter(genres__slug=genre_slug)
    if language and language.lower() != 'all':
        movies = movies.filter(language__icontains=language)
    if status_filter:
        movies = movies.filter(status=status_filter)
    if search_query:
        from django.db.models import Q
        movies = movies.filter(Q(title__icontains=search_query) | Q(genre__icontains=search_query) | Q(cast__icontains=search_query))

    genres = Genre.objects.all()
    languages = ['English', 'Malayalam', 'Hindi', 'Tamil']

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'genres': genres,
        'languages': languages,
        'selected_genre': genre_slug,
        'selected_language': language,
        'selected_status': status_filter,
        'search_query': search_query,
        'total_count': movies.count(),
    })


def movie_detail(request, tmdb_id=None, slug=None):
    """
    Full Movie Details Page:
    Displays banner, poster, title, description, genre, duration, release date,
    language, certification, rating, cast and crew, trailer playback,
    and available cinemas, dates, and showtimes.
    """
    if slug:
        movie = get_object_or_404(Movie, slug=slug)
    else:
        movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    city = request.GET.get('city') or request.session.get('selected_city') or 'Kochi'
    selected_date_str = request.GET.get('date')

    today = date.today()
    date_options = []
    for i in range(7):
        d = today + timedelta(days=i)
        date_options.append({
            'date_str': d.strftime('%Y-%m-%d'),
            'day_name': 'Today' if i == 0 else ('Tomorrow' if i == 1 else d.strftime('%a')),
            'day_num': d.strftime('%d'),
            'month': d.strftime('%b'),
            'is_selected': (selected_date_str == d.strftime('%Y-%m-%d')) or (not selected_date_str and i == 0)
        })

    active_date = selected_date_str if selected_date_str else today.strftime('%Y-%m-%d')

    # Get cinemas in city
    cinemas = Cinema.objects.filter(city__iexact=city).order_by('-rating')
    if not cinemas.exists():
        cinemas = Cinema.objects.all().order_by('-rating')

    cinema_shows = []
    for c in cinemas:
        shows = list(Show.objects.filter(
            movie=movie,
            cinema=c,
            show_date=active_date
        ).select_related('screen').order_by('show_time'))

        if shows:
            cinema_shows.append({
                'cinema': c,
                'shows': shows
            })

    # Legacy theatre showtimes support
    theatre_showtimes = []
    theatres = Theatre.objects.filter(city__iexact=city)
    if not theatres.exists():
        theatres = Theatre.objects.all()
    for t in theatres:
        st_list = list(Showtime.objects.filter(
            movie=movie,
            theatre=t,
            show_date=active_date
        ).order_by('show_time'))
        if st_list:
            theatre_showtimes.append({
                'theatre': t,
                'showtimes': st_list
            })

    # Cast list split helper
    cast_list = [c.strip() for c in movie.cast.split(',') if c.strip()] if movie.cast else []

    return render(request, 'movies/detail.html', {
        'movie': movie,
        'cinema_shows': cinema_shows,
        'theatre_showtimes': theatre_showtimes,
        'date_options': date_options,
        'active_date': active_date,
        'city': city,
        'cast_list': cast_list,
    })


def cineverse_experience(request):
    """
    Renders the futuristic 6-screen WebGL 3D Cinema Experience
    """
    return render(request, 'cineverse_experience.html')

