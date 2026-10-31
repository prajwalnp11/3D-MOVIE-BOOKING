import uuid
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from movies.models import Movie
from movies.serializers import MovieSerializer
from theatres.models import Theatre, Showtime, Seat
from theatres.serializers import TheatreSerializer, ShowtimeSerializer, SeatSerializer
from bookings.models import Snack, Booking, BookingSeat, BookingSnack
from bookings.serializers import SnackSerializer, BookingDetailSerializer


class MovieListAPIView(generics.ListAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        queryset = Movie.objects.all().order_by('-rating')
        trending = self.request.query_params.get('trending')
        genre = self.request.query_params.get('genre')
        search = self.request.query_params.get('search')

        if trending and trending.lower() in ['true', '1']:
            queryset = queryset.filter(is_trending=True)
        if genre and genre.lower() != 'all':
            queryset = queryset.filter(genre__icontains=genre)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset


class MovieDetailAPIView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    lookup_field = 'tmdb_id'


class TheatreListAPIView(generics.ListAPIView):
    serializer_class = TheatreSerializer

    def get_queryset(self):
        queryset = Theatre.objects.all().order_by('-rating')
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__iexact=city)
        return queryset


class ShowtimeListAPIView(generics.ListAPIView):
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        queryset = (
            Showtime.objects
            .select_related('movie', 'theatre')
            .order_by('show_date', 'show_time')
        )
        movie_id = self.request.query_params.get('movie_id')
        theatre_id = self.request.query_params.get('theatre_id')
        show_date = self.request.query_params.get('date')
        city = self.request.query_params.get('city')

        if movie_id:
            queryset = queryset.filter(movie__tmdb_id=movie_id)
        if theatre_id:
            queryset = queryset.filter(theatre_id=theatre_id)
        if show_date:
            queryset = queryset.filter(show_date=show_date)
        if city:
            queryset = queryset.filter(theatre__city__iexact=city)
        return queryset


class ShowtimeSeatsAPIView(APIView):
    """
    Returns real-time 3D seat availability for a given showtime.
    """
    def get(self, request, showtime_id):
        showtime = get_object_or_404(
            Showtime.objects.select_related('movie', 'theatre'),
            id=showtime_id
        )

        # Get all seats for this theatre
        seats = Seat.objects.filter(theatre=showtime.theatre, is_active=True).order_by('row', 'number')

        # Get booked seat IDs for this showtime
        booked_seat_ids = set(
            BookingSeat.objects.filter(
                booking__showtime=showtime,
                booking__status='CONFIRMED'
            ).values_list('seat_id', flat=True)
        )

        seats_data = []
        for seat in seats:
            # Apply showtime format price multiplier if applicable
            calculated_price = float(round(Decimal(seat.price) * showtime.price_multiplier, 2))
            seats_data.append({
                'id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'seat_label': f"{seat.row}{seat.number}",
                'category': seat.category,
                'category_display': seat.get_category_display(),
                'price': calculated_price,
                'x': seat.x,
                'y': seat.y,
                'z': seat.z,
                'is_booked': seat.id in booked_seat_ids
            })

        return Response({
            'showtime': {
                'id': showtime.id,
                'movie_id': showtime.movie.tmdb_id,
                'movie_title': showtime.movie.title,
                'movie_poster': showtime.movie.poster_url,
                'trailer_url': showtime.movie.trailer_url,
                'video_trailer_mp4': showtime.movie.video_trailer_mp4,
                'theatre_name': showtime.theatre.name,
                'theatre_location': showtime.theatre.location,
                'city': showtime.theatre.city,
                'screen_name': showtime.screen_name,
                'show_date': showtime.show_date.strftime('%Y-%m-%d'),
                'show_time': showtime.show_time.strftime('%I:%M %p'),
                'format_type': showtime.format_type,
            },
            'seats': seats_data,
            'total_seats': len(seats_data),
            'available_seats': sum(1 for s in seats_data if not s['is_booked']),
            'booked_seats_count': len(booked_seat_ids)
        })


class SnackListAPIView(generics.ListAPIView):
    queryset = Snack.objects.all().order_by('category', 'price')
    serializer_class = SnackSerializer


class BookingCreateAPIView(APIView):
    """
    Creates a new booking with selected seats and snacks.
    """
    @transaction.atomic
    def post(self, request):
        showtime_id = request.data.get('showtime_id')
        seat_ids = request.data.get('seat_ids', [])
        snacks_data = request.data.get('snacks', [])  # list of {id, quantity}
        customer_name = request.data.get('customer_name', 'CineVerse Guest')
        customer_email = request.data.get('customer_email', 'guest@cineverse.io')
        customer_phone = request.data.get('customer_phone', '+91 99999 88888')
        payment_method = request.data.get('payment_method', 'UPI')

        if not showtime_id:
            return Response({'error': 'showtime_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not seat_ids or len(seat_ids) == 0:
            return Response({'error': 'Please select at least one seat.'}, status=status.HTTP_400_BAD_REQUEST)

        showtime = get_object_or_404(Showtime, id=showtime_id)

        # Check if any selected seat is already booked
        already_booked = BookingSeat.objects.filter(
            booking__showtime=showtime,
            booking__status='CONFIRMED',
            seat_id__in=seat_ids
        ).select_related('seat')

        if already_booked.exists():
            labels = [f"{bs.seat.row}{bs.seat.number}" for bs in already_booked]
            return Response({
                'error': f"Seats {', '.join(labels)} have already been reserved by another guest. Please choose different seats."
            }, status=status.HTTP_409_CONFLICT)

        # Fetch seats and calculate seat subtotal
        seats = Seat.objects.filter(id__in=seat_ids, theatre=showtime.theatre)
        if len(seats) != len(seat_ids):
            return Response({'error': 'One or more seat IDs are invalid for this theatre.'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal_seats = Decimal('0.00')
        seat_booking_list = []
        for seat in seats:
            price = round(Decimal(seat.price) * showtime.price_multiplier, 2)
            subtotal_seats += price
            seat_booking_list.append((seat, price))

        # Fetch snacks and calculate snack subtotal
        subtotal_snacks = Decimal('0.00')
        snack_booking_list = []
        for s_item in snacks_data:
            s_id = s_item.get('id')
            qty = int(s_item.get('quantity', 0))
            if qty > 0 and s_id:
                try:
                    snack = Snack.objects.get(id=s_id)
                    item_total = snack.price * qty
                    subtotal_snacks += item_total
                    snack_booking_list.append((snack, qty, snack.price))
                except Snack.DoesNotExist:
                    pass

        convenience_fee = Decimal('45.00')
        tax_amount = round(convenience_fee * Decimal('0.18'), 2)  # 18% GST on convenience fee
        total_amount = subtotal_seats + subtotal_snacks + convenience_fee + tax_amount

        booking_id = f"CNV-{uuid.uuid4().hex[:6].upper()}"
        qr_code_data = f"CINEVERSE:{booking_id}:{showtime.theatre.name}:{showtime.show_date}:{total_amount}"

        user = request.user if request.user.is_authenticated else None

        booking = Booking.objects.create(
            user=user,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            showtime=showtime,
            booking_id=booking_id,
            subtotal_seats=subtotal_seats,
            subtotal_snacks=subtotal_snacks,
            convenience_fee=convenience_fee,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status='CONFIRMED',
            payment_method=payment_method,
            qr_code_data=qr_code_data,
        )

        for seat, price in seat_booking_list:
            BookingSeat.objects.create(
                booking=booking,
                seat=seat,
                price_at_booking=price
            )

        for snack, qty, price in snack_booking_list:
            BookingSnack.objects.create(
                booking=booking,
                snack=snack,
                quantity=qty,
                price_at_booking=price
            )

        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookingDetailAPIView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingDetailSerializer
    lookup_field = 'booking_id'
