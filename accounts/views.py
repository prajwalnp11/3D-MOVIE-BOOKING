from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from bookings.models import Booking


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CINEVERSE, {user.username}! Your VIP profile is active.")
            return redirect('home')
        else:
            messages.error(request, "Registration error. Please check the fields below.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been safely logged out. See you soon!")
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    user_bookings = Booking.objects.filter(
        models_user_condition(request.user)
    ).order_by('-created_at')

    return render(request, 'accounts/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'user_bookings': user_bookings,
    })


def models_user_condition(user):
    from django.db.models import Q
    return Q(user=user) | Q(customer_email=user.email)


@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    # Permission check: must belong to logged in user or have matching email
    if booking.user != request.user and booking.customer_email != request.user.email and not request.user.is_staff:
        messages.error(request, "You do not have permission to cancel this booking.")
        return redirect('my_bookings')

    if not booking.can_cancel():
        messages.error(request, "This booking can no longer be cancelled. Cancellations must be made at least 2 hours prior to showtime.")
        return redirect('booking_ticket', booking_id=booking_id)

    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.save()
        messages.success(request, f"Booking {booking.booking_id} has been cancelled successfully. Refund initiated to original payment method.")
        return redirect('my_bookings')

    return render(request, 'bookings/cancel_confirm.html', {'booking': booking})
