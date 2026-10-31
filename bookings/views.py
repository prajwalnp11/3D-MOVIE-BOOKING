import uuid
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from movies.models import Movie
from theatres.models import Theatre, Showtime, Seat
from cinemas.models import Cinema, Screen, Seat as CinemaSeat, Show
from bookings.models import Snack, Booking, BookingSeat, BookingSnack
from payments.services import PaymentGatewayService


def booking_home(request):
    showtime_id = request.GET.get('showtime')
    movie_id = request.GET.get('movie')

    movies = Movie.objects.all().order_by('-rating')

    showtimes = (
        Showtime.objects
        .filter(show_date__gte=timezone.localdate())
        .select_related('movie', 'theatre')
        .order_by('show_date', 'show_time')
    )

    selected_showtime = None
    if showtime_id:
        selected_showtime = showtimes.filter(id=showtime_id).first()
    elif movie_id:
        selected_showtime = showtimes.filter(movie__tmdb_id=movie_id).first()

    if not selected_showtime:
        selected_showtime = showtimes.first()

    snacks = Snack.objects.all().order_by('category', 'price')

    return render(request, 'bookings/booking.html', {
        'movies': movies,
        'showtimes': showtimes,
        'selected_showtime': selected_showtime,
        'snacks': snacks,
    })


def booking_auditorium(request, showtime_id):
    showtime = get_object_or_404(
        Showtime.objects.select_related('movie', 'theatre'),
        id=showtime_id
    )
    movies = Movie.objects.all().order_by('-rating')
    showtimes = (
        Showtime.objects
        .filter(show_date__gte=timezone.localdate())
        .select_related('movie', 'theatre')
        .order_by('show_date', 'show_time')
    )
    snacks = Snack.objects.all().order_by('category', 'price')

    return render(request, 'bookings/booking.html', {
        'movies': movies,
        'showtimes': showtimes,
        'selected_showtime': showtime,
        'snacks': snacks,
    })


def checkout_view(request):
    """
    Dedicated Checkout Page:
    Displays movie details, cinema details, show date, showtime, selected seats,
    ticket price, convenience fee, taxes, and final amount.
    """
    show_id = request.GET.get('show_id') or request.POST.get('show_id')
    seat_ids_raw = request.GET.get('seat_ids') or request.POST.get('seat_ids')

    if not show_id or not seat_ids_raw:
        messages.warning(request, "Please select show and seats to proceed to checkout.")
        return redirect('cinema_list')

    # Convert comma-separated or list of seat IDs
    if isinstance(seat_ids_raw, str):
        seat_id_list = [int(s.strip()) for s in seat_ids_raw.split(',') if s.strip().isdigit()]
    else:
        seat_id_list = [int(s) for s in seat_ids_raw]

    show = get_object_or_404(
        Show.objects.select_related('movie', 'cinema', 'screen'),
        id=show_id
    )
    seats = CinemaSeat.objects.filter(id__in=seat_id_list, screen=show.screen)

    # Check for already booked seats
    already_booked = BookingSeat.objects.filter(
        booking__show=show,
        booking__status='CONFIRMED',
        cinema_seat__in=seats
    ).exists()

    if already_booked:
        messages.error(request, "One or more of your chosen seats were already booked. Please reselect.")
        return redirect('seat_selection', show_id=show.id)

    # Calculate subtotals
    ticket_subtotal = sum(s.price for s in seats)
    convenience_fee = Decimal('45.00')
    tax_amount = round(convenience_fee * Decimal('0.18'), 2)
    grand_total = ticket_subtotal + convenience_fee + tax_amount

    snacks = Snack.objects.filter(is_bestseller=True)[:4]

    return render(request, 'bookings/checkout.html', {
        'show': show,
        'seats': seats,
        'seat_ids_str': ','.join(str(s.id) for s in seats),
        'ticket_subtotal': ticket_subtotal,
        'convenience_fee': convenience_fee,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
        'snacks': snacks,
    })


@transaction.atomic
def process_payment_view(request):
    """
    Processes simulated payment with race-condition seat validation and creates records.
    """
    if request.method != 'POST':
        return redirect('cinema_list')

    show_id = request.POST.get('show_id')
    seat_ids_str = request.POST.get('seat_ids', '')
    customer_name = request.POST.get('customer_name', 'CineVerse Guest').strip() or 'CineVerse Guest'
    customer_email = request.POST.get('customer_email', 'guest@cineverse.io').strip() or 'guest@cineverse.io'
    customer_phone = request.POST.get('customer_phone', '+91 98765 43210').strip() or '+91 98765 43210'
    payment_method = request.POST.get('payment_method', 'UPI')

    seat_id_list = [int(s.strip()) for s in seat_ids_str.split(',') if s.strip().isdigit()]

    if not show_id or not seat_id_list:
        messages.error(request, "Invalid booking request.")
        return redirect('cinema_list')

    show = get_object_or_404(Show, id=show_id)
    seats = list(CinemaSeat.objects.select_for_update().filter(id__in=seat_id_list, screen=show.screen))

    # Race condition check
    already_booked = BookingSeat.objects.filter(
        booking__show=show,
        booking__status='CONFIRMED',
        cinema_seat__in=seats
    )
    if already_booked.exists():
        labels = [bs.seat_label for bs in already_booked]
        messages.error(request, f"Seats {', '.join(labels)} were just reserved by another user. Please pick different seats.")
        return redirect('seat_selection', show_id=show.id)

    ticket_subtotal = sum(s.price for s in seats)
    convenience_fee = Decimal('45.00')
    tax_amount = round(convenience_fee * Decimal('0.18'), 2)
    grand_total = ticket_subtotal + convenience_fee + tax_amount

    booking_id = f"CNV-{uuid.uuid4().hex[:6].upper()}"
    qr_code_data = f"CINEVERSE-PASS:{booking_id}:{show.cinema.name}:{show.show_date}:{grand_total}"

    user = request.user if request.user.is_authenticated else None

    # Create Booking
    booking = Booking.objects.create(
        user=user,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        show=show,
        booking_id=booking_id,
        subtotal_seats=ticket_subtotal,
        convenience_fee=convenience_fee,
        tax_amount=tax_amount,
        total_amount=grand_total,
        status='CONFIRMED',
        payment_method=payment_method,
        qr_code_data=qr_code_data
    )

    # Create BookingSeat records
    for s in seats:
        BookingSeat.objects.create(
            booking=booking,
            cinema_seat=s,
            price_at_booking=s.price
        )

    # Process Payment via Payment Gateway Service
    PaymentGatewayService.capture_payment(
        booking=booking,
        payment_method=payment_method,
        amount=grand_total
    )

    messages.success(request, f"Payment authorized successfully! Your booking {booking_id} is confirmed.")
    return redirect('booking_confirmation', booking_id=booking_id)


def booking_confirmation_view(request, booking_id):
    """
    Booking Confirmation Screen with e-ticket, mock QR code, and printable view.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('show__movie', 'show__cinema', 'show__screen', 'showtime__movie', 'showtime__theatre')
        .prefetch_related('booked_seats__cinema_seat', 'booked_seats__seat'),
        booking_id=booking_id
    )

    return render(request, 'bookings/confirmation.html', {
        'booking': booking
    })


def booking_ticket(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related(
            'show__movie', 'show__cinema', 'show__screen',
            'showtime__movie', 'showtime__theatre'
        ).prefetch_related('booked_seats__cinema_seat', 'booked_seats__seat', 'booked_snacks__snack'),
        booking_id=booking_id
    )

    return render(request, 'bookings/ticket.html', {
        'booking': booking
    })


def my_bookings(request):
    user = request.user if request.user.is_authenticated else None
    if user:
        from django.db.models import Q
        bookings = Booking.objects.filter(Q(user=user) | Q(customer_email=user.email)).order_by('-created_at')
    else:
        bookings = Booking.objects.all().order_by('-created_at')[:5]

    return render(request, 'bookings/my_bookings.html', {
        'bookings': bookings
    })
