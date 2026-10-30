from django.db import models


class Theatre(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Showtime(models.Model):
    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE
    )

    theatre = models.ForeignKey(
        Theatre,
        on_delete=models.CASCADE
    )

    show_date = models.DateField()
    show_time = models.TimeField()

    def __str__(self):
        return f"{self.movie} - {self.show_date} {self.show_time}"


class Seat(models.Model):

    CATEGORY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('PREMIUM', 'Premium'),
        ('RECLINER', 'Recliner'),
    ]

    theatre = models.ForeignKey(
        Theatre,
        on_delete=models.CASCADE
    )

    row = models.CharField(max_length=2)
    number = models.IntegerField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.row}{self.number} - {self.category}"