from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def favicon_view(request):
    return HttpResponse(
        b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">\xf0\x9f\x8e\xac</text></svg>',
        content_type='image/svg+xml'
    )

urlpatterns = [
    path('favicon.ico', favicon_view, name='favicon'),
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
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'