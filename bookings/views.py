from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from movies.models import Movie
from theatres.models import Theatre, Showtime, Seat
from bookings.models import Snack, Booking, BookingSeat, BookingSnack


def booking_home(request):
    showtime_id = request.GET.get('showtime')
    movie_id = request.GET.get('movie')

    movies = Movie.objects.all().order_by('-rating')

    showtimes = (
        Showtime.objects
        .filter(show_date__gte=timezone.localdate())
        .select_related('movie', 'theatre')
        .order_by('show_date', 'show_time')
    )

    selected_showtime = None
    if showtime_id:
        selected_showtime = showtimes.filter(id=showtime_id).first()
    elif movie_id:
        selected_showtime = showtimes.filter(movie__tmdb_id=movie_id).first()

    if not selected_showtime:
        selected_showtime = showtimes.first()

    snacks = Snack.objects.all().order_by('category', 'price')

    return render(request, 'bookings/booking.html', {
        'movies': movies,
        'showtimes': showtimes,
        'selected_showtime': selected_showtime,
        'snacks': snacks,
    })


def booking_auditorium(request, showtime_id):
    showtime = get_object_or_404(
        Showtime.objects.select_related('movie', 'theatre'),
        id=showtime_id
    )
    movies = Movie.objects.all().order_by('-rating')
    showtimes = (
        Showtime.objects
        .filter(show_date__gte=timezone.localdate())
        .select_related('movie', 'theatre')
        .order_by('show_date', 'show_time')
    )
    snacks = Snack.objects.all().order_by('category', 'price')

    return render(request, 'bookings/booking.html', {
        'movies': movies,
        'showtimes': showtimes,
        'selected_showtime': showtime,
        'snacks': snacks,
    })


def booking_ticket(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related(
            'showtime__movie',
            'showtime__theatre'
        ).prefetch_related('booked_seats__seat', 'booked_snacks__snack'),
        booking_id=booking_id
    )

    return render(request, 'bookings/ticket.html', {
        'booking': booking
    })


def my_bookings(request):
    bookings = Booking.objects.all().select_related(
        'showtime__movie',
        'showtime__theatre'
    ).prefetch_related('booked_seats__seat', 'booked_snacks__snack').order_by('-created_at')

    return render(request, 'bookings/my_bookings.html', {
        'bookings': bookings
    })
