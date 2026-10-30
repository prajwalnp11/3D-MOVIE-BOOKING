from django.db import models


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=True)
    trailer_url = models.URLField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.title