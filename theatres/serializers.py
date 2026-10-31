from rest_framework import serializers
from .models import Theatre, Showtime, Seat
from movies.serializers import MovieSerializer


class TheatreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theatre
        fields = [
            'id',
            'name',
            'location',
            'city',
            'address',
            'specs',
            'rating',
        ]


class ShowtimeSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_poster = serializers.CharField(source='movie.poster_url', read_only=True)
    theatre_name = serializers.CharField(source='theatre.name', read_only=True)
    theatre_city = serializers.CharField(source='theatre.city', read_only=True)
    theatre_specs = serializers.CharField(source='theatre.specs', read_only=True)

    class Meta:
        model = Showtime
        fields = [
            'id',
            'movie',
            'movie_title',
            'movie_poster',
            'theatre',
            'theatre_name',
            'theatre_city',
            'theatre_specs',
            'screen_name',
            'show_date',
            'show_time',
            'format_type',
            'price_multiplier',
            'status',
        ]


class SeatSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    seat_label = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = [
            'id',
            'row',
            'number',
            'seat_label',
            'category',
            'category_display',
            'price',
            'x',
            'y',
            'z',
            'is_active',
        ]

    def get_seat_label(self, obj):
        return f"{obj.row}{obj.number}"
