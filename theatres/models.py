from django.db import models


class Theatre(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100, default='Kochi')
    address = models.CharField(max_length=255, blank=True)
    specs = models.CharField(max_length=200, default='IMAX 3D, 4K Laser, Dolby Atmos 7.1')
    rating = models.FloatField(default=4.8)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Showtime(models.Model):
    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='showtimes'
    )
    theatre = models.ForeignKey(
        Theatre,
        on_delete=models.CASCADE,
        related_name='showtimes'
    )
    screen_name = models.CharField(max_length=100, default='Screen 1 - IMAX')
    show_date = models.DateField()
    show_time = models.TimeField()
    format_type = models.CharField(max_length=50, default='IMAX 3D')
    price_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    status = models.CharField(
        max_length=20,
        default='AVAILABLE',
        choices=[
            ('AVAILABLE', 'Available'),
            ('FILLING_FAST', 'Filling Fast'),
            ('SOLD_OUT', 'Sold Out')
        ]
    )

    def __str__(self):
        return f"{self.movie.title} @ {self.theatre.name} - {self.show_date} {self.show_time}"


class Seat(models.Model):
    CATEGORY_CHOICES = [
        ('ROYAL', 'Royal Recliner'),
        ('BALCONY', 'Balcony'),
        ('PRIME', 'Prime'),
        ('CLASSIC', 'Classic'),
        ('RECLINER', 'Recliner'),
        ('PREMIUM', 'Premium'),
        ('VIP', 'Box / VIP'),
    ]

    CATEGORY_PRICES = {
        'ROYAL': 450,
        'BALCONY': 350,
        'PRIME': 250,
        'CLASSIC': 180,
        'RECLINER': 450,
        'PREMIUM': 300,
        'VIP': 600,
    }

    theatre = models.ForeignKey(
        Theatre,
        on_delete=models.CASCADE,
        related_name='seats'
    )
    row = models.CharField(max_length=2)
    number = models.IntegerField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='PRIME'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=250.00
    )
    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)
    z = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.price or self.price == 0:
            self.price = self.CATEGORY_PRICES.get(self.category, 250)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.row}{self.number} - {self.get_category_display()}"

