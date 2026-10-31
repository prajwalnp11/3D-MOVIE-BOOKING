from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication & User Profiles
    path('accounts/', include('accounts.urls')),

    # Movies (Home, listings, details)
    path('', include('movies.urls')),

    # Cinemas & Screen/Seat Selection
    path('cinemas/', include('cinemas.urls')),

    # Multiplex Theatres (Alternative/Legacy route)
    path('theatres/', include('theatres.urls')),

    # Bookings & Checkout Flow
    path('booking/', include('bookings.urls')),

    # REST APIs
    path('api/', include('movies.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'