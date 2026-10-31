from django.contrib import admin
from .models import Cinema, Screen, Seat, Show


class ScreenInline(admin.TabularInline):
    model = Screen
    extra = 1
    fields = ('name', 'screen_type', 'total_seats')


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0
    fields = ('row', 'number', 'category', 'price', 'is_active')
    ordering = ('row', 'number')


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'location', 'rating', 'screen_count', 'seat_count')
    list_filter = ('city',)
    search_fields = ('name', 'location', 'city', 'facilities')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ScreenInline]

    def screen_count(self, obj):
        return obj.screens.count()
    screen_count.short_description = 'Screens'

    def seat_count(self, obj):
        return obj.seats.count()
    seat_count.short_description = 'Total Seats'


@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ('name', 'cinema', 'screen_type', 'total_seats')
    list_filter = ('screen_type', 'cinema__city', 'cinema')
    search_fields = ('name', 'cinema__name')
    inlines = [SeatInline]


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_label', 'screen', 'cinema', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active', 'screen__cinema', 'row')
    search_fields = ('row', 'screen__name', 'cinema__name')
    list_editable = ('category', 'price', 'is_active')
    ordering = ('screen', 'row', 'number')
    list_per_page = 50

    def seat_label(self, obj):
        return f"{obj.row}{obj.number}"
    seat_label.short_description = 'Seat'


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('movie', 'cinema', 'screen', 'show_date', 'show_time', 'format_type', 'base_price', 'status')
    list_filter = ('show_date', 'format_type', 'status', 'cinema__city', 'cinema')
    search_fields = ('movie__title', 'cinema__name', 'screen__name')
    ordering = ('show_date', 'show_time')
    list_editable = ('status', 'base_price')
