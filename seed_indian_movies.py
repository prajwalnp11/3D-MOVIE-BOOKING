import os
import django
import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from movies.models import Movie, Genre
from theatres.models import Theatre, Showtime, Seat
from cinemas.models import Cinema, Screen, Show, Seat as CinemaSeat

today = timezone.localdate()

print(f"Seeding Indian movies and showtimes for {today} onwards...")

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

# 2. Indian Movies Data (Now Released & Running in Theatres with Real TMDB Data)
INDIAN_MOVIES = [
    {
        'tmdb_id': 1014214,
        'title': 'Singham Again',
        'rating': 8.6,
        'duration_mins': 168,
        'language': 'Hindi',
        'certification': 'UA 16+',
        'genre': 'Action / Cop Drama',
        'cast': 'Ajay Devgn, Kareena Kapoor Khan, Deepika Padukone, Ranveer Singh, Akshay Kumar, Tiger Shroff, Arjun Kapoor',
        'crew': 'Rohit Shetty',
        'description': 'DCP Bajirao Singham leads India\'s apex cop universe on an explosive cross-border mission to rescue his wife Avni from a ruthless terror cartel.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/2JbNkHg8m7LaBy61LyrnnlenaxY.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/yLKkuYMcibmNEvb97I4t6eDSSwk.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=MD7v0-igVIM',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 980599,
        'title': 'Bhool Bhulaiyaa 3',
        'rating': 8.4,
        'duration_mins': 158,
        'language': 'Hindi',
        'certification': 'UA 13+',
        'genre': 'Comedy / Horror',
        'cast': 'Kartik Aaryan, Vidya Balan, Madhuri Dixit, Triptii Dimri, Rajpal Yadav',
        'crew': 'Anees Bazmee',
        'description': 'Rooh Baba arrives in the royal kingdom of Raktaghat, West Bengal, to confront the sinister return of Manjulika and centuries-old royal curses.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/3AfHD1HoaQpQwKH8kxRdBKVmzeU.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/1TdCtQaAqZhKRSOSbPi1EPToJxN.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=fqc364gMbxI',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 927342,
        'title': 'Amaran',
        'rating': 9.0,
        'duration_mins': 167,
        'language': 'Tamil',
        'certification': 'UA 16+',
        'genre': 'Action / War / Biopic',
        'cast': 'Sivakarthikeyan, Sai Pallavi, Bhuvan Arora, Rahul Bose',
        'crew': 'Rajkumar Periasamy, Kamal Haasan, G.V. Prakash Kumar',
        'description': 'The gripping true-life saga of Major Mukund Varadarajan AC and his courageous 44 Rashtriya Rifles battalion defending peace in Jammu & Kashmir.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/kcspKUpofalIuPgAndZOMJz0hwg.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/7cNE2qydew1c8fqnlhWjkE3DHc2.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=hylIXfZeB4c',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 622792,
        'title': 'Kanguva',
        'rating': 8.2,
        'duration_mins': 154,
        'language': 'Tamil',
        'certification': 'UA 16+',
        'genre': 'Epic Fantasy / Action',
        'cast': 'Suriya, Bobby Deol, Disha Patani, Yogi Babu',
        'crew': 'Siva, Devi Sri Prasad',
        'description': 'An ancient tribal warlord fighting for his island people\'s survival is mysteriously linked across 700 years to a relentless modern bounty hunter.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/lycbTFBXqFN1kMdPEsnAFutKEEy.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/cpK4ZqGZVJAIIKo8EgpSHif8yNL.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=ajnCMSC4VPo',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 857598,
        'title': 'Pushpa 2: The Rule',
        'rating': 9.2,
        'duration_mins': 180,
        'language': 'Telugu',
        'certification': 'UA 16+',
        'genre': 'Action / Crime Thriller',
        'cast': 'Allu Arjun, Rashmika Mandanna, Fahadh Faasil, Sunil, Jagapathi Babu',
        'crew': 'Sukumar, Devi Sri Prasad',
        'description': 'Pushpa Raj commands the red sanders syndicates with an iron fist, triggering an explosive psychological feud with SP Bhanwar Singh Shekhawat.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/1T21FblunT0y8fz7YaW8JMYgUKm.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/7jGItf7idJsBm9QTNoTNTU3KiGe.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=1kVK0MZlbI4',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 811941,
        'title': 'Devara: Part 1',
        'rating': 8.5,
        'duration_mins': 177,
        'language': 'Telugu',
        'certification': 'UA 16+',
        'genre': 'Action / Coastal Drama',
        'cast': 'N.T. Rama Rao Jr., Janhvi Kapoor, Saif Ali Khan, Prakash Raj',
        'crew': 'Koratala Siva, Anirudh Ravichander',
        'description': 'A fearless coastal defender battles internal betrayal and ocean-bound smugglers to protect his island folk from annihilation.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/lQfuaXjANoTsdx5iS0gCXlK9D2L.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/hAQnXxOwCjgYcKRgTdYPRC8neqL.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=HNYA6bqL6bU',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 801688,
        'title': 'Kalki 2898 AD',
        'rating': 8.7,
        'duration_mins': 181,
        'language': 'Telugu',
        'certification': 'UA 13+',
        'genre': 'Sci-Fi / Mythological Epic',
        'cast': 'Prabhas, Amitabh Bachchan, Kamal Haasan, Deepika Padukone, Disha Patani',
        'crew': 'Nag Ashwin, Santhosh Narayanan',
        'description': 'In a post-apocalyptic dystopian Kasi in 2898 AD, immortal warrior Ashwatthama protects the carrier of the divine tenth avatar from the supreme ruler Yaskin.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/rstcAnBeCkxNQjNp3YXrF6IP1tW.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/seAIZLEq2Il2psjMUREDbSdRmbu.jpg',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=ilY1xnyOOUE',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 1112426,
        'title': 'Stree 2',
        'rating': 8.6,
        'duration_mins': 147,
        'language': 'Hindi',
        'certification': 'UA 16+',
        'genre': 'Horror / Comedy',
        'cast': 'Shraddha Kapoor, Rajkummar Rao, Pankaj Tripathi, Abhishek Banerjee, Aparshakti Khurana',
        'crew': 'Amar Kaushik',
        'description': 'The small town of Chanderi is plagued by a menacing headless spirit Sarkata, forcing Vicky and his eccentric gang to seek the aid of their guardian ghost Stree.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/nfnhwfUEFuSOxxf4jDdBlY6Lccw.jpg',
        'backdrop_url': 'https://image.tmdb.org/t/p/original/fVV0A67kDjTTQ4CvUn8LoletRmI.jpg',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=VlvOgk5BHS4',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    }
]

created_movies = []
for m_data in INDIAN_MOVIES:
    m, created = Movie.objects.update_or_create(
        tmdb_id=m_data['tmdb_id'],
        defaults=m_data
    )
    created_movies.append(m)
    print(f"Movie ready: {m.title} ({m.language}) - {m.status}")

# 3. Also update all existing movies showtimes to current/future dates so all movies have running shows
all_theatres = list(Theatre.objects.all())
all_cinemas = list(Cinema.objects.all())

show_times_pool = [
    datetime.time(10, 0),
    datetime.time(11, 40),
    datetime.time(14, 15),
    datetime.time(16, 45),
    datetime.time(19, 30),
    datetime.time(22, 15)
]

# Create showtimes for today and the next 7 days for all movies
all_movies = list(Movie.objects.all())
showtime_count = 0

for day_offset in range(7):
    show_date = today + datetime.timedelta(days=day_offset)
    for m in all_movies:
        # Create at least 2 shows per movie per day in Cinemax Kolar and PVR
        for t in [theatre_kolar, all_theatres[0], all_theatres[1] if len(all_theatres) > 1 else theatre_kolar]:
            for st_time in [datetime.time(11, 40), datetime.time(19, 30)]:
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
                showtime_count += 1

print(f"Created/Verified {showtime_count} active showtimes starting from {today}!")
