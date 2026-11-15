import os
import django
import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from movies.models import Movie, Genre
from theatres.models import Theatre, Showtime
from cinemas.models import Cinema, Screen, Show

today = timezone.localdate()
print(f"Seeding Sandalwood (Kannada) Blockbusters for {today} onwards...")

# 1. Ensure Cinemax IMAX, Kolar exists
theatre_kolar, _ = Theatre.objects.get_or_create(
    name='Cinemax IMAX: Kolar',
    defaults={
        'location': 'MG Road, Kolar',
        'city': 'Kolar',
        'address': 'Cinemax Central Multiplex, Kolar, Karnataka',
        'specs': 'IMAX 3D Laser, Dolby Atmos 12-Channel',
        'rating': 4.9
    }
)

cinema_kolar, _ = Cinema.objects.get_or_create(
    name='Cinemax IMAX: Kolar',
    defaults={
        'location': 'MG Road, Kolar',
        'city': 'Kolar',
        'address': 'Cinemax Central Multiplex, Kolar, Karnataka',
        'facilities': '4K Laser, Dolby Atmos, Valet Parking, Recliner Seats, Gourmet Lounge',
        'rating': 4.9,
        'image_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80'
    }
)

screen_kolar, _ = Screen.objects.get_or_create(
    cinema=cinema_kolar,
    name='Screen 1 - IMAX Laser',
    defaults={'screen_type': 'IMAX', 'total_seats': 60}
)

# 2. Authentic Sandalwood (Kannada) Blockbusters Data
SANDALWOOD_MOVIES = [
    {
        'tmdb_id': 777292,
        'title': 'Bagheera',
        'rating': 9.1,
        'duration_mins': 158,
        'language': 'Kannada',
        'certification': 'UA 16+',
        'genre': 'Action / Vigilante Thriller',
        'cast': 'Srii Murali, Rukmini Vasanth, Prakash Raj, Rangayana Raghu, Achyuth Kumar',
        'crew': 'D. Suri, Prashanth Neel, B. Ajaneesh Loknath',
        'description': 'IPS officer Vedanth Prabhakar transforms into the masked vigilante Bagheera by night, waging a brutal war against corrupt syndicates and human traffickers in Mangalore.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/1oyfAHvzk95XCHdQDFvpYgqvLUd.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/r9GXAvybRDx613LzNRnZAPJyjrI.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=CEfYokG1SF8',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 1088410,
        'title': 'Bhairathi Ranagal',
        'rating': 9.0,
        'duration_mins': 152,
        'language': 'Kannada',
        'certification': 'UA 16+',
        'genre': 'Action / Crime Drama',
        'cast': 'Dr. Shiva Rajkumar, Rahul Bose, Rukmini Vasanth, Devaraj, Chikkanna',
        'crew': 'Narthan, Ravi Basrur',
        'description': 'The gripping origin chronicle of Ronapura’s revered godfather Bhairathi Ranagal, revealing how an idealistic advocate rose to command the criminal underworld to safeguard his people.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/ghA56IEkZ1FwJVDWWEihtVnRYvZ.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/13yVuhVKCiN2vUa4PdKSsBFF4nh.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=Toq88y-7x1o',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 858485,
        'title': 'Kantara',
        'rating': 9.4,
        'duration_mins': 148,
        'language': 'Kannada',
        'certification': 'UA 16+',
        'genre': 'Action / Mythological Thriller',
        'cast': 'Rishab Shetty, Sapthami Gowda, Kishore, Achyuth Kumar, Pramod Shetty',
        'crew': 'Rishab Shetty, B. Ajaneesh Loknath',
        'description': 'When centuries-old tribal traditions clash with greedy landlords and forest rangers in coastal Karnataka, a Kambala champion Shiva channels the divine spirits of Panjurli and Guliga.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/jIsKmkxMzdCZ0Ux1GVSnu8m6Na6.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/kXElm7wt2kAXEVwJqW4cFhP43nW.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=MTECjlKUgEE',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 587412,
        'title': 'K.G.F: Chapter 2',
        'rating': 9.5,
        'duration_mins': 168,
        'language': 'Kannada',
        'certification': 'UA 16+',
        'genre': 'Action / Period Epic',
        'cast': 'Yash, Sanjay Dutt, Raveena Tandon, Srinidhi Shetty, Prakash Raj',
        'crew': 'Prashanth Neel, Ravi Basrur',
        'description': 'Rocky establishes his absolute rule over the blood-soaked gold mines of Kolar Gold Fields, confronting the monstrous warlord Adheera and Indian government forces.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/khNVygolU0TxLIDWff5tQlAhZ23.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/nsV5Mfi9FAV4w8eDsdr7uqVswOk.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=JKa05nyUmuQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 861451,
        'title': 'Martin',
        'rating': 8.5,
        'duration_mins': 150,
        'language': 'Kannada',
        'certification': 'UA 16+',
        'genre': 'Action / Patriotic Thriller',
        'cast': 'Dhruva Sarja, Vaibhavi Shandilya, Anveshi Jain, Sukrutha Wagle, Nikitin Dheer',
        'crew': 'A. P. Arjun, Mani Sharma, Ravi Basrur',
        'description': 'Lt. Brigadier Arjun Saxena battles ruthless international terror cartels across Pakistan and Europe while piecing together his true identity as Martin.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/rmCJCFrEwPC0u0Y1smihwDo4Cf1.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/mVtc8uLWtqwqorHl8UkhtxWNUJo.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=fqLCas2sWW0',
        'status': 'NOW_SHOWING',
        'is_featured': False,
        'is_trending': True,
    },
    {
        'tmdb_id': 634120,
        'title': '777 Charlie',
        'rating': 9.2,
        'duration_mins': 164,
        'language': 'Kannada',
        'certification': 'U',
        'genre': 'Adventure / Drama',
        'cast': 'Rakshit Shetty, Charlie, Sangeetha Sringeri, Raj B. Shetty, Danish Sait',
        'crew': 'Kiranraj K, Nobin Paul',
        'description': 'Dharma, a solitary factory worker drowning in loneliness, sets out on an unforgettable cross-country motorcycle pilgrimage to the Himalayas after rescuing a lively Labrador pup.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/qArPmXH0aWsT3SEtYl8XrU2Oz48.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/3Sdi32wfIIOtDz1hYik6bGe1iWC.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=Z3r7f9zw-mo',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 984500,
        'title': 'UI The Movie',
        'rating': 8.8,
        'duration_mins': 145,
        'language': 'Kannada',
        'certification': 'UA 16+',
        'genre': 'Sci-Fi / Political Satire',
        'cast': 'Upendra, Reeshma Nanaiah, Murali Sharma, Sadhu Kokila, Nidhi Subbaiah',
        'crew': 'Upendra, B. Ajaneesh Loknath',
        'description': 'Real Star Upendra unveils a groundbreaking mind-bending satirical spectacle interrogating universal reality, artificial truth, and societal blindness.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/tWoeysV4ro6wn4TE0QgqMuo6Val.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/3ZW8D196Ckh683dqKZMEH2Vnb8B.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=eGx2kFakx44',
        'status': 'NOW_SHOWING',
        'is_featured': False,
        'is_trending': True,
    },
    {
        'tmdb_id': 1212788,
        'title': 'Kaatera',
        'rating': 8.9,
        'duration_mins': 183,
        'language': 'Kannada',
        'certification': 'UA 16+',
        'genre': 'Action / Period Drama',
        'cast': 'Darshan, Aradhana Ram, Jagapathi Babu, Kumar Govind, Shruti',
        'crew': 'Tharun Sudhir, V. Harikrishna',
        'description': 'Set in 1970s rural Karnataka, a valiant village blacksmith Kaatera takes on feudal overlords to ensure underprivileged farmers secure their rightful ancestral land ownership.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/iP7pN1Y9OBE2D9unv2Bfwv8c3R1.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/f4zJ9UPZYrL9mMIzJEhJneP4bM1.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=lVuuwNQg74M',
        'status': 'NOW_SHOWING',
        'is_featured': False,
        'is_trending': True,
    }
]

created_movies = []
for m_data in SANDALWOOD_MOVIES:
    m, _ = Movie.objects.update_or_create(
        tmdb_id=m_data['tmdb_id'],
        defaults=m_data
    )
    created_movies.append(m)
    print(f"✔ Ready: {m.title} ({m.language}) - TMDB {m.tmdb_id} - Poster: {m.poster_url}")

# 3. Create active showtimes from today onwards
all_theatres = list(Theatre.objects.all())
all_cinemas = list(Cinema.objects.all())

showtimes_added = 0
for day_offset in range(7):
    show_date = today + datetime.timedelta(days=day_offset)
    for m in created_movies:
        for t in [theatre_kolar, all_theatres[0]]:
            for st_time in [datetime.time(11, 40), datetime.time(15, 30), datetime.time(19, 45)]:
                st, _ = Showtime.objects.get_or_create(
                    movie=m,
                    theatre=t,
                    show_date=show_date,
                    show_time=st_time,
                    defaults={
                        'screen_name': 'Screen 1 - IMAX Laser 3D',
                        'format_type': 'IMAX 3D' if 'Action' in m.genre else 'Dolby Atmos',
                        'status': 'AVAILABLE',
                        'price_multiplier': Decimal('1.00')
                    }
                )
                showtimes_added += 1

        # Also create Show for modern cinema model
        for c in [cinema_kolar, all_cinemas[0] if all_cinemas else cinema_kolar]:
            for st_time in [datetime.time(11, 40), datetime.time(19, 45)]:
                Show.objects.get_or_create(
                    cinema=c,
                    screen=screen_kolar,
                    movie=m,
                    show_date=show_date,
                    show_time=st_time,
                    defaults={
                        'format_type': 'IMAX 3D Laser',
                        'status': 'AVAILABLE'
                    }
                )

print(f"Successfully seeded {len(created_movies)} Sandalwood movies and {showtimes_added} active showtimes starting {today}!")
