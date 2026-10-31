from decimal import Decimal
from datetime import date, time
from django.test import TestCase, Client
from django.urls import reverse
from movies.models import Movie
from theatres.models import Theatre, Showtime, Seat
from bookings.models import Snack, Booking, BookingSeat, BookingSnack


class CineVerseFullStackTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Movie
        self.movie = Movie.objects.create(
            tmdb_id=155,
            title='The Dark Knight',
            description='Batman faces the Joker.',
            rating=9.0,
            genre='Action / Crime',
            duration_mins=152,
            age_rating='UA 16+',
            poster_url='https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
            backdrop_url='https://image.tmdb.org/t/p/original/dqK9Hag1054tghRQSqLSfrkvQnA.jpg',
            video_trailer_mp4='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
            is_trending=True
        )

        # 2. Theatre
        self.theatre = Theatre.objects.create(
            name='PVR ICON: Lulu Mall',
            location='Edappally, Kochi',
            city='Kochi',
            address='3rd Floor, Lulu Mall, Kochi',
            specs='IMAX 3D Laser, Dolby Atmos 7.1',
            rating=4.9
        )

        # 3. 3D Tiered Seats with coordinates
        self.seat_f1 = Seat.objects.create(
            theatre=self.theatre,
            row='F',
            number=1,
            category='ROYAL',
            price=Decimal('450.00'),
            x=-6.2,
            y=1.5,
            z=3.65
        )
        self.seat_f2 = Seat.objects.create(
            theatre=self.theatre,
            row='F',
            number=2,
            category='ROYAL',
            price=Decimal('450.00'),
            x=-4.8,
            y=1.5,
            z=3.65
        )
        self.seat_c1 = Seat.objects.create(
            theatre=self.theatre,
            row='C',
            number=1,
            category='PRIME',
            price=Decimal('250.00'),
            x=-6.2,
            y=0.6,
            z=-1.3
        )

        # 4. Showtime
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            theatre=self.theatre,
            screen_name='Audi 1 - IMAX',
            show_date=date.today(),
            show_time=time(18, 45),
            format_type='IMAX 3D',
            price_multiplier=Decimal('1.00'),
            status='AVAILABLE'
        )

        # 5. Snack
        self.popcorn = Snack.objects.create(
            name='Truffle Butter Popcorn',
            category='POPCORN',
            description='Warm popcorn with truffle butter',
            price=Decimal('280.00'),
            is_veg=True,
            is_bestseller=True
        )

    def test_homepage_view(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'CINE')
        self.assertContains(resp, 'The Dark Knight')
        self.assertContains(resp, 'PVR ICON')

    def test_theatre_selection_view(self):
        resp = self.client.get(reverse('theatre_selection') + '?city=Kochi')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Multiplex Theatres')
        self.assertContains(resp, 'PVR ICON: Lulu Mall')

    def test_movie_detail_view(self):
        resp = self.client.get(reverse('movie_detail', args=[self.movie.tmdb_id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'The Dark Knight')
        self.assertContains(resp, 'Audi 1 - IMAX')

    def test_booking_auditorium_view(self):
        resp = self.client.get(reverse('booking_auditorium', args=[self.showtime.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'theatre3D')
        self.assertContains(resp, 'Grab a Bite')

    def test_api_movie_list(self):
        resp = self.client.get('/api/movies/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]['title'], 'The Dark Knight')

    def test_api_showtime_seats(self):
        resp = self.client.get(f'/api/showtimes/{self.showtime.id}/seats/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_seats'], 3)
        self.assertEqual(data['available_seats'], 3)
        self.assertEqual(data['showtime']['movie_title'], 'The Dark Knight')

        # Check coordinates and tier on seat
        seat0 = data['seats'][0]
        self.assertIn('x', seat0)
        self.assertIn('y', seat0)
        self.assertIn('z', seat0)
        self.assertIn('category', seat0)
        self.assertFalse(seat0['is_booked'])

    def test_api_booking_creation_and_conflict(self):
        payload = {
            'showtime_id': self.showtime.id,
            'seat_ids': [self.seat_f1.id, self.seat_f2.id],
            'snacks': [{'id': self.popcorn.id, 'quantity': 1}],
            'customer_name': 'Bruce Wayne',
            'customer_email': 'bruce@wayne.com',
            'customer_phone': '+91 98888 77777',
            'payment_method': 'CyberPay'
        }

        # 1. Successful booking
        resp = self.client.post('/api/bookings/create/', data=payload, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        booking_id = data['booking_id']
        self.assertTrue(booking_id.startswith('CNV-'))
        self.assertEqual(len(data['booked_seats']), 2)
        self.assertEqual(len(data['booked_snacks']), 1)

        # Seat subtotal: 450 + 450 = 900
        # Snack subtotal: 280
        # Fee: 45, Tax: 8.10
        # Total: 1233.10
        self.assertEqual(Decimal(str(data['total_amount'])), Decimal('1233.10'))

        # 2. Duplicate seat reservation conflict check
        conflict_payload = {
            'showtime_id': self.showtime.id,
            'seat_ids': [self.seat_f1.id], # already booked!
            'customer_name': 'Two Face',
            'customer_email': 'harvey@gotham.gov'
        }
        resp_conflict = self.client.post('/api/bookings/create/', data=conflict_payload, content_type='application/json')
        self.assertEqual(resp_conflict.status_code, 409)

        # 3. Check seat availability updated in API
        resp_seats = self.client.get(f'/api/showtimes/{self.showtime.id}/seats/')
        seats_data = resp_seats.json()['seats']
        f1_seat = next(s for s in seats_data if s['id'] == self.seat_f1.id)
        self.assertTrue(f1_seat['is_booked'])

        # 4. Check digital e-ticket view
        resp_ticket = self.client.get(reverse('booking_ticket', args=[booking_id]))
        self.assertEqual(resp_ticket.status_code, 200)
        self.assertContains(resp_ticket, booking_id)
        self.assertContains(resp_ticket, 'Bruce Wayne')
        self.assertContains(resp_ticket, 'F1')
        self.assertContains(resp_ticket, 'F2')
