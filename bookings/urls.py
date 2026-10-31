from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_home, name='booking_home'),
    path('<int:showtime_id>/', views.booking_auditorium, name='booking_auditorium'),
    path('ticket/<str:booking_id>/', views.booking_ticket, name='booking_ticket'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]
