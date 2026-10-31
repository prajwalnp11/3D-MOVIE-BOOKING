from django.contrib import admin
from .models import Genre, Movie


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'rating',
        'genre',
        'duration_mins',
        'certification',
        'language',
        'status',
        'is_trending',
        'is_featured',
        'release_date'
    )
    list_filter = ('status', 'is_trending', 'is_featured', 'certification', 'language', 'release_date')
    search_fields = ('title', 'genre', 'cast', 'crew')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)