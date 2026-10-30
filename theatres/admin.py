from django.contrib import admin
from .models import Theatre, Showtime, Seat


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0


@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')
    inlines = [SeatInline]


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theatre', 'show_date', 'show_time')
    list_filter = ('show_date', 'theatre')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('theatre', 'row', 'number', 'category', 'price')
    list_filter = ('category', 'theatre')