from django.urls import path
from . import views

urlpatterns = [
    path('', views.theatre_selection, name='theatre_selection'),
]
