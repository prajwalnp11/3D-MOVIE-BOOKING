import os
import django
from decimal import Decimal
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from movies.models import Movie, Genre
from cinemas.models import Cinema, Screen, Seat, Show
from theatres.models import Theatre, Showtime
from django.utils.text import slugify

def populate_cinemas():
    print("Populating Cinemas, Screens, Seats, Shows, and Genres...")

    # 1. Genres
    genres_list = [
        'Action', 'Sci-Fi', 'Thriller', 'Crime', 'Animation',
        'Adventure', 'Fantasy', 'Mystery', 'Drama', 'Horror', 'Comedy'
    ]
    genre_objs = {}
    for g_name in genres_list:
        g, _ = Genre.objects.get_or_create(name=g_name)
        genre_objs[g_name] = g
    print(f"Created {len(genre_objs)} Genres.")

    # 2. Enrich Movies with slugs, genres, cast, crew, language, status
    movie_extra = {
        'The Dark Knight': {
            'language': 'English',
            'certification': 'UA 16+',
            'cast': 'Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine, Gary Oldman, Morgan Freeman',
            'crew': 'Christopher Nolan (Director), Emma Thomas (Producer)',
            'status': 'NOW_SHOWING',
            'is_featured': True,
            'is_trending': True,
            'genre_names': ['Action', 'Crime', 'Thriller']
        },
        'Wildwood': {
            'language': 'English',
            'certification': 'U',
            'cast': 'Peyton Elizabeth Lee, Jacob Tremblay, Carey Mulligan, Mahershala Ali, Awkwafina',
            'crew': 'Travis Knight (Director), Arianne Sutner (Producer)',
            'status': 'NOW_SHOWING',
            'is_featured': True,
            'is_trending': True,
            'genre_names': ['Animation', 'Adventure', 'Fantasy']
        },
        'Spider-Man: Brand New Day': {
            'language': 'English',
            'certification': 'UA 13+',
            'cast': 'Tom Holland, Zendaya, Jacob Batalon, Mark Ruffalo',
            'crew': 'Destin Daniel Cretton (Director), Kevin Feige (Producer)',
            'status': 'TRENDING',
            'is_featured': True,
            'is_trending': True,
            'genre_names': ['Action', 'Sci-Fi', 'Adventure']
        },
        'Hope': {
            'language': 'English / Korean',
            'certification': 'UA 16+',
            'cast': 'Hwang Jung-min, Jo In-sung, Jung Ho-yeon, Alicia Vikander, Michael Fassbender',
            'crew': 'Na Hong-jin (Director)',
            'status': 'NOW_SHOWING',
            'is_featured': False,
            'is_trending': True,
            'genre_names': ['Sci-Fi', 'Mystery', 'Thriller']
        },
        'Fall 2: Deadpoint': {
            'language': 'English',
            'certification': 'A 18+',
            'cast': 'Grace Caroline Currey, Virginia Gardner',
            'crew': 'Scott Mann (Director)',
            'status': 'UPCOMING',
            'is_featured': False,
            'is_trending': False,
            'genre_names': ['Thriller']
        },
        'Clayface': {
            'language': 'English',
            'certification': 'A 18+',
            'cast': 'Bill Skarsgard, Colin Farrell',
            'crew': 'Mike Flanagan (Director)',
            'status': 'UPCOMING',
            'is_featured': False,
            'is_trending': False,
            'genre_names': ['Action', 'Horror', 'Crime']
        },
    }

    for m in Movie.objects.all():
        if not m.slug:
            base_slug = slugify(m.title) or f"movie-{m.id}"
            slug = base_slug
            idx = 1
            while Movie.objects.filter(slug=slug).exclude(id=m.id).exists():
                slug = f"{base_slug}-{idx}"
                idx += 1
            m.slug = slug

        extra = movie_extra.get(m.title, {})
        if extra:
            m.language = extra.get('language', m.language)
            m.certification = extra.get('certification', m.certification)
            m.cast = extra.get('cast', m.cast)
            m.crew = extra.get('crew', m.crew)
            m.status = extra.get('status', 'NOW_SHOWING')
            m.is_featured = extra.get('is_featured', False)
            m.is_trending = extra.get('is_trending', True)

            for g_name in extra.get('genre_names', []):
                if g_name in genre_objs:
                    m.genres.add(genre_objs[g_name])
        else:
            if not m.cast:
                m.cast = 'Leading Ensemble Cast, Featured Artists'
            if not m.crew:
                m.crew = 'Visionary Director, Executive Producers'
            if not m.genres.exists():
                m.genres.add(genre_objs['Action'])
        m.save()
    print("Movies updated with slugs, genres, cast, crew, and statuses.")

    # 3. Populate Cinemas
    cinemas_data = [
        {
            'name': 'PVR ICON: Lulu Mall',
            'location': 'Edappally, Kochi',
            'city': 'Kochi',
            'address': '3rd Floor, Lulu International Shopping Mall, Edappally, Kochi',
            'facilities': 'IMAX 3D Laser, Dolby Atmos 7.1, 4K RGB, Recliner Lounges, Valet Parking',
            'rating': 4.9,
            'image_url': 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Cinepolis: Centre Square Mall',
            'location': 'MG Road, Kochi',
            'city': 'Kochi',
            'address': 'Level 6, Centre Square Mall, MG Road, Ernakulam, Kochi',
            'facilities': 'Macro XE Screen, Dolby Atmos, RealD 3D, Gourmet Bites, Wheelchair Access',
            'rating': 4.7,
            'image_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Shenoys Multiplex',
            'location': 'MG Road, Kochi',
            'city': 'Kochi',
            'address': 'Shenoys Junction, MG Road, Ernakulam, Kochi',
            'facilities': '4K Laser RGB, Barco 3D, Dolby Atmos, Plush Rocker Seats, Cafeteria',
            'rating': 4.8,
            'image_url': 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'PVR: Forum Mall',
            'location': 'Maradu, Kochi',
            'city': 'Kochi',
            'address': 'Forum Mall, Kundannoor, Maradu, Kochi',
            'facilities': 'P[XL] Premium Giant Screen, 4K Laser, Atmos 12-Channel, Valet',
            'rating': 4.8,
            'image_url': 'https://images.unsplash.com/photo-1595769816263-9b910be24d5f?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'PVR IMAX: Vega City',
            'location': 'Bannerghatta Road, Bengaluru',
            'city': 'Bengaluru',
            'address': 'Vega City Mall, 4th Floor, Srinivas Nagar, Bengaluru',
            'facilities': 'IMAX 3D Laser, 12-Channel Immersive Sound, Luxury Recliners',
            'rating': 4.9,
            'image_url': 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'PVR INOX: Jio World Drive',
            'location': 'BKC, Bandra East, Mumbai',
            'city': 'Mumbai',
            'address': 'Jio World Drive, Bandra Kurla Complex, Mumbai',
            'facilities': 'Maison INOX, Dolby Atmos, 4K Laser, Butler On Call, Valet',
            'rating': 4.9,
            'image_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80',
        },
    ]

    cinemas_list = []
    for c_data in cinemas_data:
        cinema, _ = Cinema.objects.update_or_create(
            name=c_data['name'],
            defaults=c_data
        )
        cinemas_list.append(cinema)
    print(f"Created/Updated {len(cinemas_list)} Cinemas.")

    # 4. Populate Screens and Seats for each cinema
    # Screen 1: IMAX, Screen 2: Atmos, Screen 3: Standard
    seat_tier_map = {
        'A': ('SILVER', Decimal('150.00')),
        'B': ('SILVER', Decimal('150.00')),
        'C': ('GOLD', Decimal('250.00')),
        'D': ('GOLD', Decimal('250.00')),
        'E': ('PREMIUM', Decimal('400.00')),
        'F': ('PREMIUM', Decimal('400.00')),
    }

    for cinema in cinemas_list:
        screen1, _ = Screen.objects.update_or_create(
            cinema=cinema,
            name='Audi 1 - IMAX Laser',
            defaults={'screen_type': 'IMAX', 'total_seats': 60}
        )
        screen2, _ = Screen.objects.update_or_create(
            cinema=cinema,
            name='Audi 2 - Dolby Atmos',
            defaults={'screen_type': 'ATMOS', 'total_seats': 60}
        )

        for screen in [screen1, screen2]:
            for row_letter, (category, price) in seat_tier_map.items():
                for num in range(1, 11):
                    Seat.objects.update_or_create(
                        screen=screen,
                        row=row_letter,
                        number=num,
                        defaults={
                            'cinema': cinema,
                            'category': category,
                            'price': price,
                            'is_active': True,
                        }
                    )
    print("Created Screens and Silver/Gold/Premium Seats.")

    # 5. Populate Shows for the upcoming 7 days
    today = date.today()
    movies = list(Movie.objects.all()[:5])
    show_times = [
        (time(10, 30), 'IMAX 3D', Decimal('200.00'), 'AVAILABLE'),
        (time(14, 15), '4K Dolby Atmos', Decimal('220.00'), 'FILLING_FAST'),
        (time(18, 45), 'IMAX 3D', Decimal('250.00'), 'FILLING_FAST'),
        (time(22, 15), '4DX 3D', Decimal('280.00'), 'AVAILABLE'),
    ]

    Show.objects.all().delete()
    total_shows = 0
    for day_idx in range(7):
        show_date = today + timedelta(days=day_idx)
        for cinema in cinemas_list:
            screens = list(cinema.screens.all())
            for movie_idx, movie in enumerate(movies[:3]):
                screen = screens[movie_idx % len(screens)]
                for st_time, fmt, base_pr, st_status in show_times:
                    Show.objects.create(
                        movie=movie,
                        cinema=cinema,
                        screen=screen,
                        show_date=show_date,
                        show_time=st_time,
                        format_type=fmt,
                        base_price=base_pr,
                        status=st_status if (day_idx > 0 or fmt != 'IMAX 3D') else 'FILLING_FAST'
                    )
                    total_shows += 1
    print(f"Generated {total_shows} Shows across 7 days for all cinemas.")
    print("Cinemas & Shows initialization COMPLETE! 🎉")

if __name__ == '__main__':
    populate_cinemas()
