from django.db import models
import uuid


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    METHOD_CHOICES = [
        ('UPI', 'Unified Payments Interface (UPI)'),
        ('CYBERPAY', 'CineVerse Fast CyberPay'),
        ('CARD', 'Credit / Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('RAZORPAY_MOCK', 'Razorpay Mock Gateway'),
    ]

    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payment'
    )
    transaction_id = models.CharField(max_length=60, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='UPI')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
    gateway_order_id = models.CharField(max_length=100, blank=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    gateway_signature = models.CharField(max_length=255, blank=True)
    response_payload = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.booking.booking_id} (₹{self.amount} - {self.status})"
