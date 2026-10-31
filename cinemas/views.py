from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import date, timedelta
from .models import Cinema, Screen, Seat, Show
from movies.models import Movie
from bookings.models import BookingSeat, Snack


def cinema_list(request):
    city = request.GET.get('city') or request.session.get('selected_city') or 'Kochi'
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

    cinemas = Cinema.objects.filter(city__iexact=city).order_by('-rating')
    if not cinemas.exists():
        cinemas = Cinema.objects.all().order_by('-rating')

    selected_movie = None
    if movie_id:
        selected_movie = Movie.objects.filter(id=movie_id).first() or Movie.objects.filter(tmdb_id=movie_id).first()

    cinema_data = []
    for c in cinemas:
        shows_qs = Show.objects.filter(
            cinema=c,
            show_date=active_date
        ).select_related('movie', 'screen')

        if selected_movie:
            shows_qs = shows_qs.filter(movie=selected_movie)

        shows_list = list(shows_qs.order_by('show_time'))

        # Calculate total available seats across today's shows
        avail_count = sum(s.screen.total_seats for s in shows_list)

        cinema_data.append({
            'cinema': c,
            'shows': shows_list,
            'has_shows': len(shows_list) > 0,
            'available_seat_count': avail_count,
        })

    movies = Movie.objects.filter(status='NOW_SHOWING').order_by('-rating')
    cities = ['Kochi', 'Bengaluru', 'Mumbai', 'Delhi-NCR', 'Hyderabad']

    return render(request, 'cinemas/cinema_list.html', {
        'cinema_data': cinema_data,
        'date_options': date_options,
        'active_date': active_date,
        'city': city,
        'cities': cities,
        'movies': movies,
        'selected_movie': selected_movie,
    })


def cinema_detail(request, slug):
    cinema = get_object_or_404(Cinema, slug=slug)
    today = date.today()
    shows = Show.objects.filter(
        cinema=cinema,
        show_date__gte=today
    ).select_related('movie', 'screen').order_by('show_date', 'show_time')

    return render(request, 'cinemas/cinema_detail.html', {
        'cinema': cinema,
        'shows': shows,
    })


def seat_selection(request, show_id):
    """
    Interactive Cinema Seat Selection View:
    - Cinema screen at top.
    - Multiple rows with Silver, Gold, Premium categories.
    - Green = available, Yellow = selected, Red = booked.
    """
    show = get_object_or_404(
        Show.objects.select_related('movie', 'cinema', 'screen'),
        id=show_id
    )

    # Get seats for this screen
    seats = Seat.objects.filter(screen=show.screen, is_active=True).order_by('row', 'number')

    # Get booked seats for this show
    booked_seat_ids = set(
        BookingSeat.objects.filter(
            booking__show=show,
            booking__status='CONFIRMED'
        ).values_list('cinema_seat_id', flat=True)
    )

    # Group seats by category and row
    rows_dict = {}
    for seat in seats:
        if seat.row not in rows_dict:
            rows_dict[seat.row] = {
                'row': seat.row,
                'category': seat.category,
                'category_display': seat.get_category_display(),
                'price': seat.price,
                'seats': []
            }
        is_booked = seat.id in booked_seat_ids
        rows_dict[seat.row]['seats'].append({
            'id': seat.id,
            'number': seat.number,
            'label': f"{seat.row}{seat.number}",
            'category': seat.category,
            'price': float(seat.price),
            'is_booked': is_booked
        })

    snacks = Snack.objects.all().order_by('category', 'price')

    return render(request, 'cinemas/seat_selection.html', {
        'show': show,
        'rows_data': list(rows_dict.values()),
        'snacks': snacks,
        'silver_price': 150,
        'gold_price': 250,
        'premium_price': 400,
    })
