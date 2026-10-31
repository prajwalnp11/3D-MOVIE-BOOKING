from django.contrib import admin
from .models import Snack, Booking, BookingSeat, BookingSnack


class BookingSeatInline(admin.TabularInline):
    model = BookingSeat
    extra = 0
    fields = ('cinema_seat', 'seat', 'price_at_booking')


class BookingSnackInline(admin.TabularInline):
    model = BookingSnack
    extra = 0
    fields = ('snack', 'quantity', 'price_at_booking')


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
        'get_movie_title',
        'get_cinema_name',
        'total_amount',
        'status',
        'payment_method',
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('booking_id', 'customer_name', 'customer_email', 'customer_phone')
    inlines = [BookingSeatInline, BookingSnackInline]

    def get_movie_title(self, obj):
        m = obj.movie
        return m.title if m else '-'
    get_movie_title.short_description = 'Movie'

    def get_cinema_name(self, obj):
        c = obj.cinema
        return c.name if c else '-'
    get_cinema_name.short_description = 'Cinema'


@admin.register(BookingSeat)
class BookingSeatAdmin(admin.ModelAdmin):
    list_display = ('booking', 'seat_label', 'category_display', 'price_at_booking')


@admin.register(BookingSnack)
class BookingSnackAdmin(admin.ModelAdmin):
    list_display = ('booking', 'snack', 'quantity', 'price_at_booking')