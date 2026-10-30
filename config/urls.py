
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Movie homepage and details
    path('', include('movies.urls')),

    # 3D movie booking
    path('booking/', include('bookings.urls')),
]
