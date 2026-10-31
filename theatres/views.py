from django.shortcuts import render
from django.utils import timezone
from datetime import date, timedelta
from movies.models import Movie
from theatres.models import Theatre, Showtime


def theatre_selection(request):
    city = request.GET.get('city', 'Kochi')
    movie_id = request.GET.get('movie')
    selected_date_str = request.GET.get('date')

    today = date.today()
    date_options = []
    for i in range(7):
        d = today + timedelta(days=i)
        date_options.append({
            'date': d,
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

    movies = Movie.objects.all().order_by('-rating')
    selected_movie = None
    if movie_id:
        selected_movie = Movie.objects.filter(tmdb_id=movie_id).first()

    theatre_showtimes = []
    for theatre in theatres:
        st_qs = Showtime.objects.filter(
            theatre=theatre,
            show_date=active_date
        ).select_related('movie')

        if selected_movie:
            st_qs = st_qs.filter(movie=selected_movie)

        showtimes_list = list(st_qs.order_by('show_time'))
        theatre_showtimes.append({
            'theatre': theatre,
            'showtimes': showtimes_list,
            'has_showtimes': len(showtimes_list) > 0
        })

    cities = ['Kochi', 'Bengaluru', 'Mumbai', 'Delhi-NCR', 'Hyderabad']

    return render(request, 'theatres/selection.html', {
        'theatre_showtimes': theatre_showtimes,
        'date_options': date_options,
        'active_date': active_date,
        'city': city,
        'cities': cities,
        'movies': movies,
        'selected_movie': selected_movie,
    })
