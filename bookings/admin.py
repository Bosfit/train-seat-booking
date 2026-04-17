from django.contrib import admin
from .models import Booking, TrainTrip


@admin.register(TrainTrip)
class TrainTripAdmin(admin.ModelAdmin):
    list_display = ("origin", "destination", "departure_time", "price", "seats_available")
    search_fields = ("origin", "destination")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_reference", "user", "trip", "seats_booked", "is_paid", "created_at")
    list_filter = ("is_paid", "created_at")
    search_fields = ("booking_reference", "user__username", "trip__origin", "trip__destination")
