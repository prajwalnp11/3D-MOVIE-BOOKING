from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import uuid


class Snack(models.Model):
    CATEGORY_CHOICES = [
        ('POPCORN', 'Popcorn'),
        ('NACHOS', 'Nachos & Dips'),
        ('BEVERAGES', 'Beverages'),
        ('COMBOS', 'Cinema Combos'),
        ('GOURMET', 'Gourmet Bites'),
    ]

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='POPCORN')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    is_veg = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (₹{self.price})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cine_bookings'
    )
    customer_name = models.CharField(max_length=120, default='CineVerse Guest')
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=30, blank=True)

    show = models.ForeignKey(
        'cinemas.Show',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bookings'
    )
    showtime = models.ForeignKey(
        'theatres.Showtime',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bookings'
    )

    booking_id = models.CharField(max_length=30, unique=True)
    subtotal_seats = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal_snacks = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    convenience_fee = models.DecimalField(max_digits=8, decimal_places=2, default=45.00)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=8.10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    payment_method = models.CharField(max_length=50, default='UPI')
    qr_code_data = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_show(self):
        return self.show or self.showtime

    @property
    def movie(self):
        if self.show:
            return self.show.movie
        if self.showtime:
            return self.showtime.movie
        return None

    @property
    def cinema(self):
        if self.show:
            return self.show.cinema
        if self.showtime:
            return self.showtime.theatre
        return None

    @property
    def screen_name(self):
        if self.show:
            return self.show.screen.name
        if self.showtime:
            return self.showtime.screen_name
        return 'Main Audi'

    @property
    def show_date(self):
        if self.show:
            return self.show.show_date
        if self.showtime:
            return self.showtime.show_date
        return None

    @property
    def show_time(self):
        if self.show:
            return self.show.show_time
        if self.showtime:
            return self.showtime.show_time
        return None

    @property
    def format_type(self):
        if self.show:
            return self.show.format_type
        if self.showtime:
            return self.showtime.format_type
        return 'IMAX 3D'

    def can_cancel(self):
        """Allows cancellation up to 2 hours before the showtime if confirmed."""
        if self.status != 'CONFIRMED':
            return False
        s_date = self.show_date
        s_time = self.show_time
        if not s_date or not s_time:
            return False
        show_datetime = datetime.combine(s_date, s_time)
        return show_datetime > datetime.now() + timedelta(hours=2)

    def __str__(self):
        return f"{self.booking_id} - {self.customer_name} (₹{self.total_amount})"


class BookingSeat(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booked_seats'
    )
    cinema_seat = models.ForeignKey(
        'cinemas.Seat',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='booked_seats'
    )
    seat = models.ForeignKey(
        'theatres.Seat',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    price_at_booking = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def resolved_seat(self):
        return self.cinema_seat or self.seat

    @property
    def seat_label(self):
        s = self.resolved_seat
        if s:
            return f"{s.row}{s.number}"
        return "Seat"

    @property
    def category_display(self):
        s = self.resolved_seat
        if s:
            return s.get_category_display()
        return "Standard"

    def __str__(self):
        return f"{self.booking.booking_id} - {self.seat_label}"


class BookingSnack(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booked_snacks'
    )
    snack = models.ForeignKey(
        Snack,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_booking = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.booking.booking_id} - {self.snack.name} x{self.quantity}"