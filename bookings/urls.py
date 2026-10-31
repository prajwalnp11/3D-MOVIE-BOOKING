from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_home, name='booking_home'),
    path('auditorium/<int:showtime_id>/', views.booking_auditorium, name='booking_auditorium'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-payment/', views.process_payment_view, name='process_payment'),
    path('confirmation/<str:booking_id>/', views.booking_confirmation_view, name='booking_confirmation'),
    path('ticket/<str:booking_id>/', views.booking_ticket, name='booking_ticket'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]
