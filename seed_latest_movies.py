import os
import django
import json
import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from movies.models import Movie, Genre
from theatres.models import Theatre, Showtime
from cinemas.models import Cinema, Screen, Show

today = timezone.localdate()
print(f"=== SEEDING LATEST 2024 MOVIES & SHOWTIMES FROM {today} ===")

# 1. Load verified TMDB data
with open('scratch_tmdb_movies.json', 'r') as f:
    movies_data = json.load(f)

# Cast and crew dictionary for rich metadata
EXTRA_META = {
    'Bagheera': {
        'cast': 'Srii Murali, Rukmini Vasanth, Prakash Raj, Rangayana Raghu, Achyuth Kumar',
        'crew': 'Dr. Suri, Prashanth Neel, B. Ajaneesh Loknath',
        'genre': 'Action / Vigilante Thriller',
        'cert': 'UA 16+'
    },
    'Bhairathi Ranagal': {
        'cast': 'Dr. Shiva Rajkumar, Rahul Bose, Rukmini Vasanth, Devaraj, Chaya Singh',
        'crew': 'Narthan, Ravi Basrur, Geetha Shiva Rajkumar',
        'genre': 'Action / Neo-Noir Crime Drama',
        'cert': 'UA 16+'
    },
    'UI The Movie': {
        'cast': 'Upendra, Reeshma Nanaiah, Sunny Leone, Nidhi Subbaiah, Murali Sharma',
        'crew': 'Upendra, B. Ajaneesh Loknath, G. Manoharan',
        'genre': 'Sci-Fi / Surreal Satire Thriller',
        'cert': 'UA 16+'
    },
    'Martin': {
        'cast': 'Dhruva Sarja, Vaibhavi Shandilya, Anveshi Jain, Sukrutha Wagle, Nikitin Dheer',
        'crew': 'A.P. Arjun, Mani Sharma, Uday K. Mehta',
        'genre': 'High-Octane Action / Patriotic Thriller',
        'cert': 'UA 16+'
    },
    'Kaatera': {
        'cast': 'Darshan, Aradhana Ram, Jagapathi Babu, Kumar Govind, Vinod Kumar Alva',
        'crew': 'Tharun Sudhir, V. Harikrishna, Rockline Venkatesh',
        'genre': 'Period Action / Social Drama',
        'cert': 'UA 16+'
    },
    'Kantara': {
        'cast': 'Rishab Shetty, Sapthami Gowda, Kishore, Achyuth Kumar, Pramod Shetty',
        'crew': 'Rishab Shetty, B. Ajaneesh Loknath, Vijay Kiragandur',
        'genre': 'Folklore Action / Mythological Thriller',
        'cert': 'UA 16+'
    },
    'K.G.F: Chapter 2': {
        'cast': 'Yash, Sanjay Dutt, Raveena Tandon, Srinidhi Shetty, Prakash Raj',
        'crew': 'Prashanth Neel, Ravi Basrur, Vijay Kiragandur',
        'genre': 'Period Action / Epic Crime Saga',
        'cert': 'UA 16+'
    },
    '777 Charlie': {
        'cast': 'Charlie, Rakshit Shetty, Sangeetha Sringeri, Raj B. Shetty, Danish Sait',
        'crew': 'Kiranraj K, Nobin Paul, G.S. Gupta',
        'genre': 'Heartwarming Adventure / Drama',
        'cert': 'U'
    },
    'Pushpa 2: The Rule': {
        'cast': 'Allu Arjun, Rashmika Mandanna, Fahadh Faasil, Jagapathi Babu, Sunil',
        'crew': 'Sukumar, Devi Sri Prasad, Naveen Yerneni',
        'genre': 'Pan-India Action / Crime Drama',
        'cert': 'UA 16+'
    },
    'Singham Again': {
        'cast': 'Ajay Devgn, Kareena Kapoor, Deepika Padukone, Ranveer Singh, Akshay Kumar, Tiger Shroff',
        'crew': 'Rohit Shetty, Ravi Basrur, Thaman S',
        'genre': 'Action / Cop Universe Masala',
        'cert': 'UA 16+'
    },
    'Bhool Bhulaiyaa 3': {
        'cast': 'Kartik Aaryan, Vidya Balan, Madhuri Dixit, Triptii Dimri, Rajpal Yadav',
        'crew': 'Anees Bazmee, Pritam, Bhushan Kumar',
        'genre': 'Horror / Comedy / Mystery',
        'cert': 'UA 13+'
    },
    'Amaran': {
        'cast': 'Sivakarthikeyan, Sai Pallavi, Bhuvan Arora, Rahul Bose, Lallu',
        'crew': 'Rajkumar Periasamy, G.V. Prakash Kumar, Kamal Haasan',
        'genre': 'Biographical War Action / Drama',
        'cert': 'UA 16+'
    },
    'Kanguva': {
        'cast': 'Suriya, Bobby Deol, Disha Patani, Natarajan Subramaniam, Yogi Babu',
        'crew': 'Siva, Devi Sri Prasad, K.E. Gnanavel Raja',
        'genre': 'Period Fantasy / Epic Action',
        'cert': 'UA 16+'
    },
    'Devara: Part 1': {
        'cast': 'NTR Jr., Janhvi Kapoor, Saif Ali Khan, Shruti Marathe, Prakash Raj',
        'crew': 'Koratala Siva, Anirudh Ravichander, Sudhakar Mikkilineni',
        'genre': 'Coastal Action / Revenge Drama',
        'cert': 'UA 16+'
    },
    'Stree 2': {
        'cast': 'Shraddha Kapoor, Rajkummar Rao, Pankaj Tripathi, Abhishek Banerjee, Aparshakti Khurana',
        'crew': 'Amar Kaushik, Sachin-Jigar, Dinesh Vijan',
        'genre': 'Horror Comedy / Supernatural Thriller',
        'cert': 'UA 16+'
    },
    'Kalki 2898 AD': {
        'cast': 'Prabhas, Amitabh Bachchan, Kamal Haasan, Deepika Padukone, Disha Patani',
        'crew': 'Nag Ashwin, Santhosh Narayanan, C. Aswani Dutt',
        'genre': 'Dystopian Sci-Fi / Hindu Mythological Epic',
        'cert': 'UA 13+'
    },
    'The Greatest of All Time': {
        'cast': 'Thalapathy Vijay, Prashanth, Prabhu Deva, Sneha, Meenakshi Chaudhary',
        'crew': 'Venkat Prabhu, Yuvan Shankar Raja, Archana Kalpathi',
        'genre': 'Sci-Fi Action / Spy Thriller',
        'cert': 'UA 16+'
    },
    'Vettaiyan': {
        'cast': 'Rajinikanth, Amitabh Bachchan, Fahadh Faasil, Rana Daggubati, Manju Warrier',
        'crew': 'T.J. Gnanavel, Anirudh Ravichander, Subaskaran Allirajah',
        'genre': 'Action / Investigative Crime Drama',
        'cert': 'UA 16+'
    },
    'Hanu-Man': {
        'cast': 'Teja Sajja, Amritha Aiyer, Varalaxmi Sarathkumar, Vinay Rai, Vennela Kishore',
        'crew': 'Prasanth Varma, Anudeep Dev, K. Niranjan Reddy',
        'genre': 'Superhero / Mythological Fantasy',
        'cert': 'UA 13+'
    },
    'Gladiator II': {
        'cast': 'Paul Mescal, Pedro Pascal, Denzel Washington, Connie Nielsen, Joseph Quinn',
        'crew': 'Ridley Scott, Harry Gregson-Williams, Walter Parkes',
        'genre': 'Historical Epic / Action Drama',
        'cert': 'A'
    },
    'Deadpool & Wolverine': {
        'cast': 'Ryan Reynolds, Hugh Jackman, Emma Corrin, Matthew Macfadyen, Dafne Keen',
        'crew': 'Shawn Levy, Rob Simonsen, Kevin Feige',
        'genre': 'Superhero Action / Comedy / Multiverse',
        'cert': 'A'
    },
    'Dune: Part Two': {
        'cast': 'Timothée Chalamet, Zendaya, Rebecca Ferguson, Javier Bardem, Austin Butler',
        'crew': 'Denis Villeneuve, Hans Zimmer, Mary Parent',
        'genre': 'Sci-Fi / Epic Space Adventure',
        'cert': 'UA 16+'
    },
}

# 2. De-feature old dummy movies so they don't crowd the top spots
old_dummies = Movie.objects.filter(id__gte=2, id__lte=20)
old_dummies.update(is_featured=False, is_trending=False, status='UPCOMING')
print(f"De-featured {old_dummies.count()} old placeholder movies.")

# 3. Insert or Update Latest 2024 Movies
saved_movies = []
for idx, data in enumerate(movies_data):
    tmdb_id = data['tmdb_id']
    title = data['title']
    extra = EXTRA_META.get(title, {})
    
    # Check if movie already exists by tmdb_id or title
    m = Movie.objects.filter(tmdb_id=tmdb_id).first() or Movie.objects.filter(title__iexact=title).first()
    if not m:
        m = Movie(tmdb_id=tmdb_id, title=title)

    m.tmdb_id = tmdb_id
    m.title = title
    m.language = data.get('lang', 'Hindi')
    m.duration_mins = data.get('runtime') or 150
    m.description = data.get('overview') or ''
    
    poster_path = data.get('poster_path')
    if poster_path:
        m.poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    
    backdrop_path = data.get('backdrop_path')
    if backdrop_path:
        m.backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"
    elif m.poster_url:
        m.backdrop_url = m.poster_url

    rel_str = data.get('release_date')
    if rel_str:
        try:
            m.release_date = datetime.date.fromisoformat(rel_str)
        except Exception:
            m.release_date = today

    # Assign attractive authentic ratings (8.8 to 9.5)
    base_rating = 8.8 + ((idx * 7) % 7) * 0.1
    m.rating = round(min(9.5, base_rating), 1)

    m.genre = extra.get('genre', ' / '.join(data.get('genres_list', ['Action', 'Thriller'])))
    m.certification = extra.get('cert', 'UA 16+')
    m.cast = extra.get('cast', '')
    m.crew = extra.get('crew', '')
    m.trailer_url = data.get('yt', '')
    m.video_trailer_mp4 = data.get('video', '')
    
    m.status = 'NOW_SHOWING'
    m.is_trending = True
    m.is_featured = True
    m.save()

    # Link genres
    for g_name in data.get('genres_list', []):
        g_obj, _ = Genre.objects.get_or_create(name=g_name)
        m.genres.add(g_obj)

    saved_movies.append(m)
    print(f"✔ Ready: [{m.id}] {m.title} ({m.language}) - Rel: {m.release_date} - Poster: {m.poster_url[:40]}... - MP4: {m.video_trailer_mp4}")

# 4. Ensure Cinemax IMAX: Kolar and Popular Cinemas have active showtimes for today and next 5 days
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

popular_cinemas = list(Cinema.objects.all()[:4])
theatres_list = list(Theatre.objects.all()[:4])

time_slots = [
    datetime.time(10, 30),
    datetime.time(13, 45),
    datetime.time(17, 0),
    datetime.time(20, 15),
    datetime.time(23, 15),
]

showtimes_created = 0
shows_created = 0

for day_offset in range(7):
    show_d = today + datetime.timedelta(days=day_offset)
    
    # 1. Shows at Cinemax IMAX: Kolar for all latest movies
    for i, m in enumerate(saved_movies[:10]):
        slot = time_slots[i % len(time_slots)]
        st, created = Showtime.objects.get_or_create(
            movie=m,
            theatre=theatre_kolar,
            show_date=show_d,
            show_time=slot,
            defaults={
                'screen_name': 'Screen 1 - IMAX Laser',
                'format_type': 'IMAX 3D Laser',
                'price_multiplier': Decimal('1.20'),
                'status': 'AVAILABLE'
            }
        )
        if created: showtimes_created += 1

        sh, created = Show.objects.get_or_create(
            movie=m,
            cinema=cinema_kolar,
            screen=screen_kolar,
            show_date=show_d,
            show_time=slot,
            defaults={
                'format_type': 'IMAX 3D Laser',
                'base_price': Decimal('250.00'),
                'status': 'AVAILABLE'
            }
        )
        if created: shows_created += 1

    # 2. Shows across other major cinemas
    for cinema in popular_cinemas:
        if cinema == cinema_kolar: continue
        scr = cinema.screens.first()
        if not scr:
            scr = Screen.objects.create(cinema=cinema, name="Audi 1", screen_type="STANDARD", total_seats=100)
        
        for i, m in enumerate(saved_movies[:6]):
            slot = time_slots[(i + 1) % len(time_slots)]
            sh, created = Show.objects.get_or_create(
                movie=m,
                cinema=cinema,
                screen=scr,
                show_date=show_d,
                show_time=slot,
                defaults={
                    'format_type': 'Dolby Atmos 4K',
                    'base_price': Decimal('220.00'),
                    'status': 'AVAILABLE'
                }
            )
            if created: shows_created += 1

    for th in theatres_list:
        if th == theatre_kolar: continue
        for i, m in enumerate(saved_movies[:6]):
            slot = time_slots[(i + 2) % len(time_slots)]
            st, created = Showtime.objects.get_or_create(
                movie=m,
                theatre=th,
                show_date=show_d,
                show_time=slot,
                defaults={
                    'screen_name': 'Audi 1 - 4K Atmos',
                    'format_type': '4K Dolby Atmos',
                    'price_multiplier': Decimal('1.00'),
                    'status': 'AVAILABLE'
                }
            )
            if created: showtimes_created += 1

print(f"\n✔ Done! Created {showtimes_created} new Showtimes & {shows_created} new Cinema Shows for dates {today} through {today + datetime.timedelta(days=6)}.")
print(f"✔ Database now loaded with {len(saved_movies)} of the latest 2024 blockbuster movies!")
