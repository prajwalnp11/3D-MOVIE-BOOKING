from django.urls import path
from . import views

urlpatterns = [
    path('', views.cinema_list, name='cinema_list'),
    path('<slug:slug>/', views.cinema_detail, name='cinema_detail'),
    path('seat-select/<int:show_id>/', views.seat_selection, name='seat_selection'),
]
