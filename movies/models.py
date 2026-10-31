from django.db import models
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Movie(models.Model):
    STATUS_CHOICES = [
        ('NOW_SHOWING', 'Now Showing'),
        ('UPCOMING', 'Upcoming'),
        ('TRENDING', 'Trending'),
    ]

    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    poster_url = models.URLField(blank=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    backdrop_url = models.URLField(blank=True)
    trailer_url = models.URLField(blank=True)
    video_trailer_mp4 = models.URLField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    rating = models.FloatField(default=0.0)
    genre = models.CharField(max_length=150, default='Action / Sci-Fi')
    genres = models.ManyToManyField(Genre, blank=True, related_name='movies')
    duration_mins = models.IntegerField(default=145)
    language = models.CharField(max_length=50, default='English')
    certification = models.CharField(max_length=20, default='UA 16+')
    cast = models.TextField(blank=True, help_text='Comma-separated actor names')
    crew = models.TextField(blank=True, help_text='Director, Producer, etc.')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOW_SHOWING')
    is_trending = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    @property
    def age_rating(self):
        return self.certification

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or f"movie-{self.tmdb_id or ''}"
            slug = base_slug
            counter = 1
            while Movie.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def get_poster(self):
        if self.poster:
            return self.poster.url
        return self.poster_url or ''

    @property
    def get_banner(self):
        if self.banner:
            return self.banner.url
        return self.backdrop_url or self.poster_url or ''

    def __str__(self):
        return self.title