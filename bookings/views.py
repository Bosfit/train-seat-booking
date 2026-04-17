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
                    # Lock the trip row so two users cannot overbook at the same time.
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
