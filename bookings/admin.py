from django.contrib import admin
from .models import Snack, Booking, BookingSeat, BookingSnack


class BookingSeatInline(admin.TabularInline):
    model = BookingSeat
    extra = 0


class BookingSnackInline(admin.TabularInline):
    model = BookingSnack
    extra = 0


@admin.register(Snack)
class SnackAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_veg', 'is_bestseller')
    list_filter = ('category', 'is_veg', 'is_bestseller')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id',
        'customer_name',
        'showtime',
        'total_amount',
        'status',
        'payment_method',
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('booking_id', 'customer_name', 'customer_email', 'customer_phone')
    inlines = [BookingSeatInline, BookingSnackInline]


@admin.register(BookingSeat)
class BookingSeatAdmin(admin.ModelAdmin):
    list_display = ('booking', 'seat', 'price_at_booking')


@admin.register(BookingSnack)
class BookingSnackAdmin(admin.ModelAdmin):
    list_display = ('booking', 'snack', 'quantity', 'price_at_booking')