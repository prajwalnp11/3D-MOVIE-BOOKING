from rest_framework import serializers
from .models import Snack, Booking, BookingSeat, BookingSnack
from theatres.models import Showtime, Seat


class SnackSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Snack
        fields = [
            'id',
            'name',
            'category',
            'category_display',
            'description',
            'price',
            'image_url',
            'is_veg',
            'is_bestseller',
        ]


class BookingSeatSerializer(serializers.ModelSerializer):
    seat_label = serializers.SerializerMethodField()
    category = serializers.CharField(source='seat.category', read_only=True)
    category_display = serializers.CharField(source='seat.get_category_display', read_only=True)

    class Meta:
        model = BookingSeat
        fields = [
            'id',
            'seat',
            'seat_label',
            'category',
            'category_display',
            'price_at_booking',
        ]

    def get_seat_label(self, obj):
        return f"{obj.seat.row}{obj.seat.number}"


class BookingSnackSerializer(serializers.ModelSerializer):
    snack_name = serializers.CharField(source='snack.name', read_only=True)
    snack_image = serializers.CharField(source='snack.image_url', read_only=True)

    class Meta:
        model = BookingSnack
        fields = [
            'id',
            'snack',
            'snack_name',
            'snack_image',
            'quantity',
            'price_at_booking',
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    booked_seats = BookingSeatSerializer(many=True, read_only=True)
    booked_snacks = BookingSnackSerializer(many=True, read_only=True)
    movie_title = serializers.CharField(source='showtime.movie.title', read_only=True)
    movie_poster = serializers.CharField(source='showtime.movie.poster_url', read_only=True)
    movie_age_rating = serializers.CharField(source='showtime.movie.age_rating', read_only=True)
    theatre_name = serializers.CharField(source='showtime.theatre.name', read_only=True)
    theatre_location = serializers.CharField(source='showtime.theatre.location', read_only=True)
    screen_name = serializers.CharField(source='showtime.screen_name', read_only=True)
    show_date = serializers.DateField(source='showtime.show_date', read_only=True)
    show_time = serializers.TimeField(source='showtime.show_time', read_only=True)
    format_type = serializers.CharField(source='showtime.format_type', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'booking_id',
            'customer_name',
            'customer_email',
            'customer_phone',
            'status',
            'payment_method',
            'subtotal_seats',
            'subtotal_snacks',
            'convenience_fee',
            'tax_amount',
            'total_amount',
            'qr_code_data',
            'created_at',
            'movie_title',
            'movie_poster',
            'movie_age_rating',
            'theatre_name',
            'theatre_location',
            'screen_name',
            'show_date',
            'show_time',
            'format_type',
            'booked_seats',
            'booked_snacks',
        ]
