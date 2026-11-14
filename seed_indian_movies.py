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

# 2. Indian Movies Data (Now Released & Running in Theatres)
INDIAN_MOVIES = [
    {
        'tmdb_id': 100001,
        'title': 'Singham Again',
        'rating': 8.6,
        'duration_mins': 168,
        'language': 'Hindi',
        'certification': 'UA 16+',
        'genre': 'Action / Cop Drama',
        'cast': 'Ajay Devgn, Kareena Kapoor Khan, Deepika Padukone, Ranveer Singh, Akshay Kumar, Tiger Shroff, Arjun Kapoor',
        'crew': 'Rohit Shetty',
        'description': 'DCP Bajirao Singham leads India\'s apex cop universe on an explosive cross-border mission to rescue his wife Avni from a ruthless terror cartel.',
        'poster_url': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 100002,
        'title': 'Bhool Bhulaiyaa 3',
        'rating': 8.4,
        'duration_mins': 158,
        'language': 'Hindi',
        'certification': 'UA',
        'genre': 'Comedy / Horror',
        'cast': 'Kartik Aaryan, Vidya Balan, Madhuri Dixit, Triptii Dimri, Rajpal Yadav',
        'crew': 'Anees Bazmee',
        'description': 'Rooh Baba arrives in the royal kingdom of Raktaghat, West Bengal, to confront the sinister return of Manjulika and centuries-old royal curses.',
        'poster_url': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 100003,
        'title': 'Amaran',
        'rating': 9.0,
        'duration_mins': 167,
        'language': 'Tamil',
        'certification': 'UA',
        'genre': 'Action / War / Biopic',
        'cast': 'Sivakarthikeyan, Sai Pallavi, Bhuvan Arora, Rahul Bose',
        'crew': 'Rajkumar Periasamy, Kamal Haasan, G.V. Prakash Kumar',
        'description': 'The gripping true-life saga of Major Mukund Varadarajan AC and his courageous 44 Rashtriya Rifles battalion defending peace in Jammu & Kashmir.',
        'poster_url': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 100004,
        'title': 'Kanguva',
        'rating': 8.2,
        'duration_mins': 154,
        'language': 'Tamil',
        'certification': 'UA 16+',
        'genre': 'Epic Fantasy / Action',
        'cast': 'Suriya, Bobby Deol, Disha Patani, Yogi Babu',
        'crew': 'Siva, Devi Sri Prasad',
        'description': 'An ancient tribal warlord fighting for his island people\'s survival is mysteriously linked across 700 years to a relentless modern bounty hunter.',
        'poster_url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 100005,
        'title': 'Pushpa 2: The Rule',
        'rating': 9.2,
        'duration_mins': 180,
        'language': 'Telugu',
        'certification': 'UA 16+',
        'genre': 'Action / Crime Thriller',
        'cast': 'Allu Arjun, Rashmika Mandanna, Fahadh Faasil, Sunil, Jagapathi Babu',
        'crew': 'Sukumar, Devi Sri Prasad',
        'description': 'Pushpa Raj commands the red sanders syndicates with an iron fist, triggering an explosive psychological feud with SP Bhanwar Singh Shekhawat.',
        'poster_url': 'https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 100006,
        'title': 'Devara: Part 1',
        'rating': 8.5,
        'duration_mins': 177,
        'language': 'Telugu',
        'certification': 'A',
        'genre': 'Action / Coastal Drama',
        'cast': 'N.T. Rama Rao Jr., Janhvi Kapoor, Saif Ali Khan, Prakash Raj',
        'crew': 'Koratala Siva, Anirudh Ravichander',
        'description': 'A fearless coastal defender battles internal betrayal and ocean-bound smugglers to protect his island folk from annihilation.',
        'poster_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 100007,
        'title': 'Kalki 2898 AD',
        'rating': 8.7,
        'duration_mins': 181,
        'language': 'Telugu',
        'certification': 'UA',
        'genre': 'Sci-Fi / Mythological Epic',
        'cast': 'Prabhas, Amitabh Bachchan, Kamal Haasan, Deepika Padukone, Disha Patani',
        'crew': 'Nag Ashwin, Santhosh Narayanan',
        'description': 'In a post-apocalyptic dystopian Kasi in 2898 AD, immortal warrior Ashwatthama protects the carrier of the divine tenth avatar from the supreme ruler Yaskin.',
        'poster_url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://vjs.zencdn.net/v/oceans.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': True,
        'is_trending': True,
    },
    {
        'tmdb_id': 100008,
        'title': 'Stree 2',
        'rating': 8.6,
        'duration_mins': 147,
        'language': 'Hindi',
        'certification': 'UA',
        'genre': 'Horror / Comedy',
        'cast': 'Shraddha Kapoor, Rajkummar Rao, Pankaj Tripathi, Abhishek Banerjee, Aparshakti Khurana',
        'crew': 'Amar Kaushik',
        'description': 'The small town of Chanderi is plagued by a menacing headless spirit Sarkata, forcing Vicky and his eccentric gang to seek the aid of their guardian ghost Stree.',
        'poster_url': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80',
        'backdrop_url': 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=1200&q=80',
        'video_trailer_mp4': 'https://media.w3.org/2010/05/sintel/trailer.mp4',
        'trailer_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'status': 'NOW_SHOWING',
        'is_featured': False,
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
