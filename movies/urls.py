from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('experience/', views.cineverse_experience, name='cineverse_experience'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movie/<int:tmdb_id>/', views.movie_detail, name='movie_detail'),
    path('movie/slug/<slug:slug>/', views.movie_detail, name='movie_detail_slug'),
]