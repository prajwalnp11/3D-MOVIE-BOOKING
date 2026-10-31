from rest_framework import serializers
from .models import Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            'id',
            'tmdb_id',
            'title',
            'description',
            'poster_url',
            'backdrop_url',
            'trailer_url',
            'video_trailer_mp4',
            'release_date',
            'rating',
            'genre',
            'duration_mins',
            'age_rating',
            'is_trending',
        ]
