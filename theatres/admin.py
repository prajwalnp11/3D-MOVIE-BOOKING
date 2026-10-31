from django.contrib import admin
from .models import Theatre, Showtime, Seat


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0
    fields = ('row', 'number', 'category', 'price', 'x', 'y', 'z', 'is_active')
    ordering = ('row', 'number')
    show_change_link = True


@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'location', 'rating', 'seat_count')
    list_filter = ('city',)
    search_fields = ('name', 'location', 'city')
    inlines = [SeatInline]

    def seat_count(self, obj):
        return obj.seats.count()

    seat_count.short_description = 'Total Seats'


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theatre', 'screen_name', 'show_date', 'show_time', 'format_type', 'status')
    list_filter = ('show_date', 'format_type', 'status', 'theatre')
    search_fields = ('movie__title', 'theatre__name', 'screen_name')
    ordering = ('show_date', 'show_time')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = (
        'theatre',
        'row',
        'number',
        'category',
        'price',
        'x',
        'y',
        'z',
        'is_active',
    )
    list_filter = (
        'theatre',
        'category',
        'row',
        'is_active',
    )
    search_fields = (
        'theatre__name',
        'row',
    )
    list_editable = ('category', 'price', 'is_active')
    ordering = ('theatre', 'row', 'number')
    list_per_page = 60
