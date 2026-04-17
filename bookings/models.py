from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TrainTrip(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    seats_available = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.origin} to {self.destination} ({self.departure_time:%Y-%m-%d %H:%M})"


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    trip = models.ForeignKey(
        TrainTrip,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    seats_booked = models.PositiveIntegerField(default=1)
    booking_reference = models.CharField(max_length=20, unique=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if not self.trip_id:
            return

        if self.trip.departure_time <= timezone.now():
            raise ValidationError("You cannot book a trip that has already departed.")

        if self.seats_booked > self.trip.seats_available:
            raise ValidationError(
                f"Only {self.trip.seats_available} seat(s) are available for this trip."
            )

    def __str__(self):
        return f"{self.booking_reference} - {self.user} - {self.trip}"
