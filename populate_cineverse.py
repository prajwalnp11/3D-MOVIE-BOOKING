import os
import django
from decimal import Decimal
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from movies.models import Movie
from theatres.models import Theatre, Showtime, Seat
from bookings.models import Snack, Booking, BookingSeat, BookingSnack

def populate():
    print("Populating CineVerse database...")

    # 1. Enrich existing movies with backdrops, genres, and trailers
    movie_meta = {
        155: {  # The Dark Knight
            'genre': 'Action / Crime / Thriller',
            'duration_mins': 152,
            'age_rating': 'UA 16+',
            'backdrop_url': 'https://image.tmdb.org/t/p/original/dqK9Hag1054tghRQSqLSfrkvQnA.jpg',
            'video_trailer_mp4': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
            'is_trending': True,
        },
        791523: {  # Wildwood
            'genre': 'Animation / Adventure / Fantasy',
            'duration_mins': 118,
            'age_rating': 'U',
            'backdrop_url': 'https://image.tmdb.org/t/p/original/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg',
            'video_trailer_mp4': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            'is_trending': True,
        },
        969681: {  # Spider-Man: Brand New Day
            'genre': 'Action / Sci-Fi / Adventure',
            'duration_mins': 148,
            'age_rating': 'UA 13+',
            'backdrop_url': 'https://image.tmdb.org/t/p/original/14QbnygCuTO0vl7CAFmPf1fgZfV.jpg',
            'video_trailer_mp4': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
            'is_trending': True,
        },
        1058424: {  # Hope
            'genre': 'Sci-Fi / Mystery / Drama',
            'duration_mins': 136,
            'age_rating': 'UA 16+',
            'backdrop_url': 'https://image.tmdb.org/t/p/original/nNAe2TkealcvzbdbeOao5r0t4G3.jpg',
            'video_trailer_mp4': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4',
            'is_trending': True,
        },
        1101412: {  # Fall 2: Deadpoint
            'genre': 'Thriller / Survival',
            'duration_mins': 115,
            'age_rating': 'A 18+',
            'backdrop_url': 'https://image.tmdb.org/t/p/original/rOmLLkUycIFz0jWwQk4Z3zG8kY.jpg',
            'video_trailer_mp4': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
            'is_trending': True,
        },
    }

    for movie in Movie.objects.all():
        meta = movie_meta.get(movie.tmdb_id, {})
        movie.genre = meta.get('genre', movie.genre or 'Action / Sci-Fi')
        movie.duration_mins = meta.get('duration_mins', movie.duration_mins or 135)
        movie.age_rating = meta.get('age_rating', movie.age_rating or 'UA 16+')
        if meta.get('backdrop_url'):
            movie.backdrop_url = meta['backdrop_url']
        elif not movie.backdrop_url and movie.poster_url:
            movie.backdrop_url = movie.poster_url
        if meta.get('video_trailer_mp4'):
            movie.video_trailer_mp4 = meta['video_trailer_mp4']
        else:
            movie.video_trailer_mp4 = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4'
        movie.is_trending = meta.get('is_trending', True)
        movie.save()
    print("Movies updated with rich metadata & backdrops.")

    # 2. Setup Theatres in Kochi, Bengaluru, Mumbai
    theatres_data = [
        {
            'name': 'PVR ICON: Lulu Mall',
            'location': 'Edappally, Kochi',
            'city': 'Kochi',
            'address': '3rd Floor, Lulu International Shopping Mall, NH 66, Edappally, Kochi',
            'specs': 'IMAX 3D Laser, Dolby Atmos 7.1, 4K RGB',
            'rating': 4.9,
        },
        {
            'name': 'Cinepolis: Centre Square Mall',
            'location': 'MG Road, Kochi',
            'city': 'Kochi',
            'address': 'Level 6, Centre Square Mall, Mahatma Gandhi Rd, Kochi',
            'specs': 'RealD 3D, Dolby Atmos, Macro XE',
            'rating': 4.7,
        },
        {
            'name': 'Shenoys Theatre',
            'location': 'MG Road, Kochi',
            'city': 'Kochi',
            'address': 'Shenoys Junction, MG Road, Ernakulam, Kochi',
            'specs': '4K Laser, Barco 3D, Dolby Atmos',
            'rating': 4.8,
        },
        {
            'name': 'PVR: Forum Mall',
            'location': 'Maradu, Kochi',
            'city': 'Kochi',
            'address': 'Forum Mall, Kundannoor, Maradu, Kochi',
            'specs': 'P[XL] Giant Screen, 4K Laser, Atmos',
            'rating': 4.8,
        },
        {
            'name': 'PVR IMAX: Vega City',
            'location': 'Bannerghatta Road, Bengaluru',
            'city': 'Bengaluru',
            'address': 'Vega City Mall, 4th Floor, Srinivas Nagar, Bengaluru',
            'specs': 'IMAX 3D Laser, 12-Channel Immersive Sound',
            'rating': 4.9,
        },
        {
            'name': 'PVR INOX: Jio World Drive',
            'location': 'BKC, Bandra East, Mumbai',
            'city': 'Mumbai',
            'address': 'Jio World Drive, Bandra Kurla Complex, Mumbai',
            'specs': 'Maison INOX, Dolby Atmos, 4K Laser',
            'rating': 4.9,
        },
    ]

    theatre_objects = []
    for t_data in theatres_data:
        theatre, _ = Theatre.objects.update_or_create(
            name=t_data['name'],
            defaults=t_data
        )
        theatre_objects.append(theatre)
    print(f"Created/Updated {len(theatre_objects)} Theatres across Kochi, Bengaluru, Mumbai.")

    # 3. Create standardized tiered 3D seats for all theatres
    # Tier structure:
    # Row A & B: CLASSIC (₹180) - rows 0, 1
    # Row C & D: PRIME (₹250) - rows 2, 3
    # Row E: BALCONY (₹350) - row 4
    # Row F: ROYAL RECLINER (₹450) - row 5
    tier_config = {
        'A': ('CLASSIC', Decimal('180.00'), 0),
        'B': ('CLASSIC', Decimal('180.00'), 1),
        'C': ('PRIME', Decimal('250.00'), 2),
        'D': ('PRIME', Decimal('250.00'), 3),
        'E': ('BALCONY', Decimal('350.00'), 4),
        'F': ('ROYAL', Decimal('450.00'), 5),
    }

    for theatre in theatre_objects:
        for row_letter, (category, price, row_idx) in tier_config.items():
            for seat_num in range(1, 11):
                # 3D coordinates:
                # x: centered across 10 seats (-6.2 to +6.2)
                # z: depth from front to back (-4.6 to +3.65)
                # y: tiered stadium elevation (0.0 to 1.5)
                x_coord = round((seat_num - 5.5) * 1.38, 2)
                z_coord = round(-4.6 + row_idx * 1.65, 2)
                y_coord = round(row_idx * 0.3, 2)

                Seat.objects.update_or_create(
                    theatre=theatre,
                    row=row_letter,
                    number=seat_num,
                    defaults={
                        'category': category,
                        'price': price,
                        'x': x_coord,
                        'y': y_coord,
                        'z': z_coord,
                        'is_active': True,
                    }
                )
    print("Tiered 3D seats with 3D coordinates generated for all theatres.")

    # 4. Generate Showtimes across upcoming days
    today = date.today()
    movies = list(Movie.objects.all()[:6])
    show_times_list = [
        (time(10, 30), 'IMAX 3D', 'AVAILABLE'),
        (time(14, 15), '4K Laser Atmos', 'FILLING_FAST'),
        (time(18, 45), 'IMAX 3D', 'FILLING_FAST'),
        (time(22, 15), '4DX 3D', 'AVAILABLE'),
    ]

    Showtime.objects.all().delete()
    showtime_count = 0
    for day_offset in range(0, 6):
        show_date = today + timedelta(days=day_offset)
        for theatre in theatre_objects:
            # Assign top 3 movies to each theatre per day
            for movie_idx, movie in enumerate(movies[:3]):
                for t_idx, (st_time, fmt, st_status) in enumerate(show_times_list):
                    # Stagger showtimes slightly
                    hour = (st_time.hour + movie_idx) % 24
                    minute = st_time.minute
                    st_time_adjusted = time(hour, minute)

                    Showtime.objects.create(
                        movie=movie,
                        theatre=theatre,
                        screen_name=f"Audi {movie_idx + 1} - {fmt}",
                        show_date=show_date,
                        show_time=st_time_adjusted,
                        format_type=fmt,
                        price_multiplier=Decimal('1.00') if fmt != 'IMAX 3D' else Decimal('1.20'),
                        status=st_status if (day_offset > 0 or t_idx != 2) else 'FILLING_FAST'
                    )
                    showtime_count += 1
    print(f"Generated {showtime_count} Showtimes across 6 days.")

    # 5. Populate Gourmet Cinema Snacks
    Snack.objects.all().delete()
    snacks_data = [
        {
            'name': 'CineVerse Truffle Butter Popcorn',
            'category': 'POPCORN',
            'description': 'Freshly popped warm golden corn tossed in real French truffle butter and Himalayan pink salt.',
            'price': Decimal('280.00'),
            'image_url': 'https://images.unsplash.com/photo-1578849278619-e73505e9610f?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': True,
        },
        {
            'name': 'Gourmet Salted Caramel Popcorn',
            'category': 'POPCORN',
            'description': 'Artisan crunchy popcorn coated in decadent melted golden caramel glaze.',
            'price': Decimal('310.00'),
            'image_url': 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': True,
        },
        {
            'name': 'Loaded Cheddar Queso Nachos',
            'category': 'NACHOS',
            'description': 'Stone-ground crispy corn tortilla chips layered with warm Mexican cheddar cheese sauce, roasted tomato salsa & jalapeños.',
            'price': Decimal('290.00'),
            'image_url': 'https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': True,
        },
        {
            'name': 'Peri Peri Spiced Nachos with Guacamole',
            'category': 'NACHOS',
            'description': 'Crisp tortilla triangles dusted with African peri peri spice, served with fresh smashed avocado guacamole.',
            'price': Decimal('340.00'),
            'image_url': 'https://images.unsplash.com/photo-1570560258879-af7f8e1447ac?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': False,
        },
        {
            'name': 'Cyber Neon Pepsi Black (750ml)',
            'category': 'BEVERAGES',
            'description': 'Ice-cold refreshing zero-sugar Pepsi Max in a souvenir CineVerse glow cup.',
            'price': Decimal('190.00'),
            'image_url': 'https://images.unsplash.com/photo-1629203851122-3726ecdf080e?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': True,
        },
        {
            'name': 'Electric Blueberry Sparkling Soda',
            'category': 'BEVERAGES',
            'description': 'Craft fizzy soda infused with wild blue berries, kaffir lime, and edible neon shimmer.',
            'price': Decimal('240.00'),
            'image_url': 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': False,
        },
        {
            'name': 'CineVerse IMAX Mega Duo Combo',
            'category': 'COMBOS',
            'description': '1 Tub Truffle Popcorn + 1 Loaded Nachos + 2 Large Pepsi + 1 Free Reusable Hologram Cup.',
            'price': Decimal('690.00'),
            'image_url': 'https://images.unsplash.com/photo-1512152272829-e3139592d56f?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': True,
        },
        {
            'name': 'Solo Gamer Snack Box',
            'category': 'COMBOS',
            'description': 'Regular Butter Popcorn + Cold Beverage + Crispy Churros with Belgian Chocolate dip.',
            'price': Decimal('490.00'),
            'image_url': 'https://images.unsplash.com/photo-1505253758473-96b301b5c81d?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': False,
        },
        {
            'name': 'Smoked Chicken & Jalapeño Hot Dog',
            'category': 'GOURMET',
            'description': 'Artisan brioche bun with smoked chicken sausage, Dijon mustard, caramelized onions & pickled jalapeños.',
            'price': Decimal('320.00'),
            'image_url': 'https://images.unsplash.com/photo-1619740455993-9e612b1af08a?auto=format&fit=crop&w=600&q=80',
            'is_veg': False,
            'is_bestseller': True,
        },
        {
            'name': 'Golden Cinnamon Churros with Nutella Dip',
            'category': 'GOURMET',
            'description': 'Warm, crispy Spanish pastry fingers tossed in cinnamon sugar with warm Belgian Nutella dip.',
            'price': Decimal('260.00'),
            'image_url': 'https://images.unsplash.com/photo-1624300629298-e9de39c13be5?auto=format&fit=crop&w=600&q=80',
            'is_veg': True,
            'is_bestseller': False,
        },
    ]

    for s_data in snacks_data:
        Snack.objects.create(**s_data)
    print(f"Created {len(snacks_data)} CineVerse Snacks.")

    # 6. Create a realistic demo booking so some seats appear Booked in 3D
    first_showtime = Showtime.objects.first()
    if first_showtime:
        booked_seat_names = ['D5', 'D6', 'F1', 'F2']
        seats_to_book = Seat.objects.filter(
            theatre=first_showtime.theatre,
            row__in=['D', 'F'],
            number__in=[1, 2, 5, 6]
        )[:4]

        booking = Booking.objects.create(
            customer_name='Alex Mercer',
            customer_email='alex.mercer@cineverse.io',
            customer_phone='+91 98765 43210',
            showtime=first_showtime,
            booking_id='CNV-884291',
            subtotal_seats=Decimal('1200.00'),
            subtotal_snacks=Decimal('590.00'),
            convenience_fee=Decimal('45.00'),
            tax_amount=Decimal('8.10'),
            total_amount=Decimal('1843.10'),
            status='CONFIRMED',
            payment_method='UPI',
            qr_code_data='VERIFIED:CNV-884291:PVR-ICON-LULU:AUDI1'
        )

        for s in seats_to_book:
            BookingSeat.objects.create(
                booking=booking,
                seat=s,
                price_at_booking=s.price
            )

        popcorn = Snack.objects.filter(category='POPCORN').first()
        if popcorn:
            BookingSnack.objects.create(
                booking=booking,
                snack=popcorn,
                quantity=2,
                price_at_booking=popcorn.price
            )
        print(f"Created demo confirmed booking {booking.booking_id} with 4 booked seats.")

    print("CineVerse database population COMPLETE! 🎉")

if __name__ == '__main__':
    populate()
