from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Movie website
    path('', include('movies.urls')),

    # Theatres & Showtimes
    path('theatres/', include('theatres.urls')),

    # Booking website
    path('booking/', include('bookings.urls')),

    # REST API
    path('api/', include('movies.api_urls')),
]