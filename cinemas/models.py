from django.db import models
from django.utils.text import slugify


class Cinema(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100, default='Kochi')
    address = models.CharField(max_length=255, blank=True)
    facilities = models.CharField(
        max_length=255,
        default='4K Laser, Dolby Atmos, Valet Parking, Recliner Seats, Gourmet Lounge'
    )
    rating = models.FloatField(default=4.8)
    image = models.ImageField(upload_to='cinemas/', blank=True, null=True)
    image_url = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Cinema.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url or 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=800&q=80'

    def __str__(self):
        return f"{self.name} ({self.city})"


class Screen(models.Model):
    SCREEN_TYPES = [
        ('IMAX', 'IMAX 3D Laser'),
        ('4DX', '4DX Motion'),
        ('ATMOS', 'Dolby Atmos 4K'),
        ('STANDARD', 'Standard Digital'),
    ]

    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='screens')
    name = models.CharField(max_length=100, default='Screen 1 - IMAX')
    screen_type = models.CharField(max_length=20, choices=SCREEN_TYPES, default='IMAX')
    total_seats = models.PositiveIntegerField(default=60)

    def __str__(self):
        return f"{self.cinema.name} - {self.name}"


class Seat(models.Model):
    CATEGORY_CHOICES = [
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PREMIUM', 'Premium Recliner'),
    ]

    CATEGORY_PRICES = {
        'SILVER': 150,
        'GOLD': 250,
        'PREMIUM': 400,
    }

    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seats')
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=2)
    number = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GOLD')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=250.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['screen', 'row', 'number'],
                name='unique_seat_per_screen'
            )
        ]
        ordering = ['row', 'number']

    def save(self, *args, **kwargs):
        if not self.price or self.price == 0:
            self.price = self.CATEGORY_PRICES.get(self.category, 250)
        super().save(*args, **kwargs)

    @property
    def seat_label(self):
        return f"{self.row}{self.number}"

    def __str__(self):
        return f"{self.screen.name} - {self.row}{self.number} ({self.category})"


class Show(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('FILLING_FAST', 'Filling Fast'),
        ('SOLD_OUT', 'Sold Out'),
    ]

    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='shows')
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='shows')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='shows')
    show_date = models.DateField()
    show_time = models.TimeField()
    format_type = models.CharField(max_length=50, default='IMAX 3D')
    base_price = models.DecimalField(max_digits=8, decimal_places=2, default=200.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

    class Meta:
        ordering = ['show_date', 'show_time']

    def __str__(self):
        return f"{self.movie.title} @ {self.cinema.name} ({self.screen.name}) - {self.show_date} {self.show_time}"
