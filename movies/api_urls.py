from django.urls import path
from .api_views import (
    MovieListAPIView,
    MovieDetailAPIView,
    TheatreListAPIView,
    ShowtimeListAPIView,
    ShowtimeSeatsAPIView,
    SnackListAPIView,
    BookingCreateAPIView,
    BookingDetailAPIView,
)

urlpatterns = [
    path('movies/', MovieListAPIView.as_view(), name='api-movie-list'),
    path('movies/<int:tmdb_id>/', MovieDetailAPIView.as_view(), name='api-movie-detail'),
    path('theatres/', TheatreListAPIView.as_view(), name='api-theatre-list'),
    path('showtimes/', ShowtimeListAPIView.as_view(), name='api-showtime-list'),
    path('showtimes/<int:showtime_id>/seats/', ShowtimeSeatsAPIView.as_view(), name='api-showtime-seats'),
    path('snacks/', SnackListAPIView.as_view(), name='api-snack-list'),
    path('bookings/create/', BookingCreateAPIView.as_view(), name='api-booking-create'),
    path('bookings/<str:booking_id>/', BookingDetailAPIView.as_view(), name='api-booking-detail'),
]
