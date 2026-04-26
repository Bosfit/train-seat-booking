from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import Booking, TrainTrip


def home(request):
    """Site home page — uses templates/bookings/home.html which extends base.html."""
    trips = TrainTrip.objects.all()
    context = {"trips": trips}
    return render(request, "bookings/home.html", context)


@login_required(login_url="accounts:login")
def create_booking(request, trip_id):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    trip = TrainTrip.objects.select_for_update().get(id=trip_id)
                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.trip = trip
                    booking.booking_reference = f"BK{uuid4().hex[:8].upper()}"
                    booking.full_clean()
                    booking.save()
                    trip.seats_available -= booking.seats_booked
                    trip.save(update_fields=["seats_available"])
            except TrainTrip.DoesNotExist:
                messages.error(request, "This trip does not exist.")
                return redirect("bookings:home")
            except ValidationError as error:
                form.add_error(None, str(error))
            else:
                messages.success(request, "Booking created successfully.")
                return redirect("bookings:my_bookings")
    else:
        form = BookingForm()
    trip = get_object_or_404(TrainTrip, id=trip_id)

    return render(
        request,
        "bookings/booking_form.html",
        {"form": form, "trip": trip},
    )


@login_required(login_url="accounts:login")
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("trip")
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})


@login_required(login_url="accounts:login")
def booking_detail(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("trip"),
        id=booking_id,
        user=request.user,
    )
    return render(request, "bookings/booking_detail.html", {"booking": booking})


@login_required(login_url="accounts:login")
def update_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("trip"),
        id=booking_id,
        user=request.user,
    )

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            try:
                with transaction.atomic():
                    trip = TrainTrip.objects.select_for_update().get(id=booking.trip_id)
                    booking = Booking.objects.select_for_update().get(id=booking.id, user=request.user)
                    old_seats = booking.seats_booked

                    updated_booking = form.save(commit=False)
                    updated_booking.user = request.user
                    updated_booking.trip = trip
                    updated_booking.full_clean()
                    updated_booking.save()

                    trip.seats_available += old_seats - updated_booking.seats_booked
                    trip.save(update_fields=["seats_available"])
            except ValidationError as error:
                form.add_error(None, str(error))
            else:
                messages.success(request, "Booking updated successfully.")
                return redirect("bookings:booking_detail", booking_id=booking.id)
    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        "bookings/booking_update.html",
        {"form": form, "booking": booking},
    )


@login_required(login_url="accounts:login")
def delete_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("trip"),
        id=booking_id,
        user=request.user,
    )

    if request.method == "POST":
        with transaction.atomic():
            trip = TrainTrip.objects.select_for_update().get(id=booking.trip_id)
            booking = Booking.objects.select_for_update().get(id=booking.id, user=request.user)
            trip.seats_available += booking.seats_booked
            trip.save(update_fields=["seats_available"])
            booking.delete()

        messages.success(request, "Booking deleted successfully.")
        return redirect("bookings:my_bookings")

    return render(request, "bookings/booking_confirm_delete.html", {"booking": booking})


@login_required(login_url="accounts:login")
def ticket_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("trip"),
        id=booking_id,
        user=request.user,
    )

    if not booking.is_paid:
        messages.warning(request, "You need to complete payment before viewing your ticket.")
        return redirect("payments:checkout", booking_id=booking.id)

    return render(request, "bookings/ticket.html", {"booking": booking})
