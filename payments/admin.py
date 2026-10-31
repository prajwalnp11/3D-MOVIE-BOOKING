from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'get_booking_id', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'booking__booking_id', 'booking__customer_name', 'booking__customer_email')
    readonly_fields = ('transaction_id', 'created_at')

    def get_booking_id(self, obj):
        return obj.booking.booking_id
    get_booking_id.short_description = 'Booking ID'
