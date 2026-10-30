
from django.shortcuts import render
from django.utils import timezone

from movies.models import Movie
from theatres.models import Showtime


def booking_home(request):
    movies = Movie.objects.all().order_by('-rating')

    showtimes = (
        Showtime.objects
        .filter(show_date__gte=timezone.localdate())
        .select_related('movie', 'theatre')
        .order_by('show_date', 'show_time')
    )

    return render(request, 'bookings/booking.html', {
        'movies': movies,
        'showtimes': showtimes,
    })
