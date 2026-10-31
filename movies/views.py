from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import date, timedelta
from .models import Movie
from theatres.models import Theatre, Showtime
from bookings.models import Snack


def home(request):
    city = request.GET.get('city', 'Kochi')
    movies = Movie.objects.all().order_by('-rating')
    trending_movies = Movie.objects.filter(is_trending=True).order_by('-rating')[:6]
    if not trending_movies.exists():
        trending_movies = movies[:5]
    featured_movie = trending_movies.first()

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

    # Theatres in current city
    theatres = Theatre.objects.filter(city__iexact=city).order_by('-rating')
    if not theatres.exists():
        theatres = Theatre.objects.all().order_by('-rating')

    theatre_showtimes = []
    for t in theatres[:3]:
        st_list = list(Showtime.objects.filter(
            theatre=t,
            show_date=today
        ).select_related('movie').order_by('show_time')[:5])
        theatre_showtimes.append({
            'theatre': t,
            'showtimes': st_list
        })

    snacks = Snack.objects.filter(is_bestseller=True)[:4]
    cities = ['Kochi', 'Bengaluru', 'Mumbai', 'Delhi-NCR', 'Hyderabad']

    return render(request, 'movies/home.html', {
        'movies': movies,
        'trending_movies': trending_movies,
        'featured_movie': featured_movie,
        'theatre_showtimes': theatre_showtimes,
        'date_options': date_options,
        'city': city,
        'cities': cities,
        'snacks': snacks,
    })


def movie_detail(request, tmdb_id):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
    city = request.GET.get('city', 'Kochi')
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

    theatres = Theatre.objects.filter(city__iexact=city).order_by('-rating')
    if not theatres.exists():
        theatres = Theatre.objects.all().order_by('-rating')

    theatre_showtimes = []
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

    cities = ['Kochi', 'Bengaluru', 'Mumbai', 'Delhi-NCR', 'Hyderabad']

    return render(request, 'movies/detail.html', {
        'movie': movie,
        'theatre_showtimes': theatre_showtimes,
        'date_options': date_options,
        'active_date': active_date,
        'city': city,
        'cities': cities,
    })
