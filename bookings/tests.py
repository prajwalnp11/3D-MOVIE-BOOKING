from decimal import Decimal
from datetime import date, time, timedelta, datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from movies.models import Movie, Genre
from theatres.models import Theatre, Showtime, Seat
from cinemas.models import Cinema, Screen, Seat as CinemaSeat, Show
from bookings.models import Snack, Booking, BookingSeat, BookingSnack


class CineVerseFullStackTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Movie & Genre
        self.genre_action = Genre.objects.create(name='Action', slug='action')
        self.movie = Movie.objects.create(
            tmdb_id=155,
            title='The Dark Knight',
            slug='the-dark-knight',
            description='Batman faces the Joker in Gotham City.',
            rating=9.0,
            genre='Action / Crime',
            duration_mins=152,
            language='English',
            certification='UA 16+',
            poster_url='https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
            backdrop_url='https://image.tmdb.org/t/p/original/dqK9Hag1054tghRQSqLSfrkvQnA.jpg',
            video_trailer_mp4='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
            status='NOW_SHOWING',
            is_trending=True,
            is_featured=True
        )
        self.movie.genres.add(self.genre_action)

        # 2. Cinema, Screen & CinemaSeats
        self.cinema = Cinema.objects.create(
            name='PVR ICON: Lulu Mall',
            slug='pvr-icon-lulu-mall',
            location='Edappally, Kochi',
            city='Kochi',
            address='3rd Floor, Lulu Mall, Kochi',
            facilities='4K Laser, Dolby Atmos, Valet Parking, Recliner Seats',
            rating=4.9
        )
        self.screen = Screen.objects.create(
            cinema=self.cinema,
            name='Audi 1 - IMAX',
            screen_type='IMAX',
            total_seats=60
        )
        self.cinema_seat_a1 = CinemaSeat.objects.create(
            screen=self.screen,
            cinema=self.cinema,
            row='A',
            number=1,
            category='SILVER',
            price=Decimal('150.00')
        )
        self.cinema_seat_a2 = CinemaSeat.objects.create(
            screen=self.screen,
            cinema=self.cinema,
            row='A',
            number=2,
            category='SILVER',
            price=Decimal('150.00')
        )
        self.cinema_seat_c1 = CinemaSeat.objects.create(
            screen=self.screen,
            cinema=self.cinema,
            row='C',
            number=1,
            category='GOLD',
            price=Decimal('250.00')
        )

        # 3. Cinema Show
        # Set showtime 5 hours ahead so cancellation rule test is predictable
        future_time = (datetime.now() + timedelta(hours=5)).time()
        self.show = Show.objects.create(
            movie=self.movie,
            cinema=self.cinema,
            screen=self.screen,
            show_date=date.today(),
            show_time=future_time,
            format_type='IMAX 3D',
            base_price=Decimal('200.00'),
            status='AVAILABLE'
        )

        # 4. Legacy Theatre & Showtime (for backward compatibility)
        self.theatre = Theatre.objects.create(
            name='PVR ICON: Lulu Mall Kochi',
            location='Edappally, Kochi',
            city='Kochi',
            address='3rd Floor, Lulu Mall, Kochi',
            specs='IMAX 3D Laser, Dolby Atmos 7.1',
            rating=4.9
        )
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

    # -------------------------------------------------------------
    # Step 4: Homepage Tests
    # -------------------------------------------------------------
    def test_homepage_view(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'CINE')
        self.assertContains(resp, 'The Dark Knight')
        self.assertContains(resp, 'PVR ICON')

    # -------------------------------------------------------------
    # Step 5: Movie Listing & Details Tests
    # -------------------------------------------------------------
    def test_movie_list_view(self):
        resp = self.client.get(reverse('movie_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'The Dark Knight')

        # Filter by genre
        resp_filtered = self.client.get(reverse('movie_list') + '?genre=action')
        self.assertEqual(resp_filtered.status_code, 200)
        self.assertContains(resp_filtered, 'The Dark Knight')

        # Filter by search
        resp_search = self.client.get(reverse('movie_list') + '?q=Knight')
        self.assertEqual(resp_search.status_code, 200)
        self.assertContains(resp_search, 'The Dark Knight')

    def test_movie_detail_view(self):
        resp = self.client.get(reverse('movie_detail', args=[self.movie.tmdb_id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'The Dark Knight')
        self.assertContains(resp, 'Audi 1 - IMAX')

    # -------------------------------------------------------------
    # Step 6: Cinema Listing & Details Tests
    # -------------------------------------------------------------
    def test_cinema_list_view(self):
        resp = self.client.get(reverse('cinema_list') + '?city=Kochi')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PVR ICON: Lulu Mall')

    def test_cinema_detail_view(self):
        resp = self.client.get(reverse('cinema_detail', args=[self.cinema.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PVR ICON: Lulu Mall')
        self.assertContains(resp, 'The Dark Knight')

    # -------------------------------------------------------------
    # Step 7: Interactive Seat Selection View
    # -------------------------------------------------------------
    def test_seat_selection_view(self):
        resp = self.client.get(reverse('seat_selection', args=[self.show.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ticket Summary')
        self.assertContains(resp, 'A1')
        self.assertContains(resp, 'Proceed to Checkout')

    # -------------------------------------------------------------
    # Step 8: Checkout View
    # -------------------------------------------------------------
    def test_checkout_view(self):
        resp = self.client.get(
            reverse('checkout') + f"?show_id={self.show.id}&seat_ids={self.cinema_seat_a1.id},{self.cinema_seat_a2.id}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Review & Confirm Your Tickets')
        self.assertContains(resp, 'The Dark Knight')
        self.assertContains(resp, 'A1')
        self.assertContains(resp, 'A2')
        # Subtotal: 150 + 150 = 300, Fee: 45, Tax: 8.10 => 353.10
        self.assertContains(resp, '353.10')

    # -------------------------------------------------------------
    # Step 9 & 10: Payment Simulation & Confirmation
    # -------------------------------------------------------------
    def test_process_payment_and_confirmation(self):
        post_data = {
            'show_id': self.show.id,
            'seat_ids': f"{self.cinema_seat_a1.id},{self.cinema_seat_a2.id}",
            'customer_name': 'Clark Kent',
            'customer_email': 'clark@dailyplanet.com',
            'customer_phone': '+91 99999 88888',
            'payment_method': 'UPI'
        }
        resp = self.client.post(reverse('process_payment'), data=post_data)
        self.assertEqual(resp.status_code, 302)

        booking = Booking.objects.filter(customer_email='clark@dailyplanet.com').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertEqual(booking.booked_seats.count(), 2)

        # Verify confirmation screen
        confirm_url = reverse('booking_confirmation', args=[booking.booking_id])
        resp_confirm = self.client.get(confirm_url)
        self.assertEqual(resp_confirm.status_code, 200)
        self.assertContains(resp_confirm, booking.booking_id)
        self.assertContains(resp_confirm, 'Clark Kent')
        self.assertContains(resp_confirm, 'A1')

        # Verify duplicate seat booking prevention
        resp_duplicate = self.client.post(reverse('process_payment'), data=post_data)
        self.assertEqual(resp_duplicate.status_code, 302)
        # Should redirect back to seat selection due to conflict
        self.assertIn(reverse('seat_selection', args=[self.show.id]), resp_duplicate.url)

    # -------------------------------------------------------------
    # Step 11: Authentication & User Dashboard
    # -------------------------------------------------------------
    def test_auth_registration_and_login(self):
        # 1. Register new user
        reg_data = {
            'username': 'dianaprince',
            'first_name': 'Diana',
            'last_name': 'Prince',
            'email': 'diana@amazon.com',
            'phone': '+91 77777 66666',
            'city': 'Mumbai',
            'password1': 'Themyscira@2026',
            'password2': 'Themyscira@2026'
        }
        resp_reg = self.client.post(reverse('register'), data=reg_data)
        self.assertEqual(resp_reg.status_code, 302)

        user = User.objects.filter(username='dianaprince').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.profile.city, 'Mumbai')

        # 2. Login
        resp_login = self.client.post(reverse('login'), data={
            'username': 'dianaprince',
            'password': 'Themyscira@2026'
        })
        self.assertEqual(resp_login.status_code, 302)

        # 3. View profile
        resp_profile = self.client.get(reverse('profile'))
        self.assertEqual(resp_profile.status_code, 200)
        self.assertContains(resp_profile, 'dianaprince')

    def test_booking_cancellation_rule(self):
        user = User.objects.create_user(username='bruce', email='bruce@wayne.com', password='password123')
        self.client.login(username='bruce', password='password123')

        # Create confirmed booking with showtime in future (> 2 hours)
        booking = Booking.objects.create(
            user=user,
            customer_name='Bruce Wayne',
            customer_email='bruce@wayne.com',
            show=self.show,
            booking_id='CNV-TEST01',
            total_amount=Decimal('353.10'),
            status='CONFIRMED'
        )
        self.assertTrue(booking.can_cancel())

        # Test cancel view POST
        resp_cancel = self.client.post(reverse('cancel_booking', args=[booking.booking_id]))
        self.assertEqual(resp_cancel.status_code, 302)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')

    # -------------------------------------------------------------
    # Legacy 3D Auditorium & API Endpoints
    # -------------------------------------------------------------
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
