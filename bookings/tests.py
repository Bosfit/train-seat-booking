from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, TrainTrip


class BookingFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="StrongPass123!")
        self.other_user = User.objects.create_user(username="other", password="StrongPass123!")
        self.future_trip = TrainTrip.objects.create(
            origin="London",
            destination="Leeds",
            departure_time=timezone.now() + timedelta(days=2),
            price="30.00",
            seats_available=10,
        )
        self.past_trip = TrainTrip.objects.create(
            origin="York",
            destination="Bristol",
            departure_time=timezone.now() - timedelta(days=1),
            price="20.00",
            seats_available=5,
        )

    def test_create_booking_reduces_trip_seats(self):
        self.client.login(username=self.user.username, password="StrongPass123!")
        response = self.client.post(
            reverse("bookings:create_booking", kwargs={"trip_id": self.future_trip.id}),
            {"seats_booked": 3},
        )

        self.assertRedirects(response, reverse("bookings:my_bookings"))
        booking = Booking.objects.get(user=self.user, trip=self.future_trip)
        self.assertEqual(booking.seats_booked, 3)
        self.future_trip.refresh_from_db()
        self.assertEqual(self.future_trip.seats_available, 7)

    def test_overbooking_is_blocked(self):
        self.client.login(username=self.user.username, password="StrongPass123!")
        response = self.client.post(
            reverse("bookings:create_booking", kwargs={"trip_id": self.future_trip.id}),
            {"seats_booked": 99},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Only 10 seat(s) are available for this trip.")
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 0)

    def test_past_trip_booking_validation_raises_error(self):
        booking = Booking(
            user=self.user,
            trip=self.past_trip,
            seats_booked=1,
            booking_reference="BKPASTTEST",
        )

        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_user_cannot_view_other_users_booking_detail(self):
        booking = Booking.objects.create(
            user=self.user,
            trip=self.future_trip,
            seats_booked=1,
            booking_reference="BKOWNR001",
        )
        self.client.login(username=self.other_user.username, password="StrongPass123!")

        response = self.client.get(
            reverse("bookings:booking_detail", kwargs={"booking_id": booking.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_unpaid_ticket_redirects_to_checkout(self):
        booking = Booking.objects.create(
            user=self.user,
            trip=self.future_trip,
            seats_booked=1,
            booking_reference="BKUNPAID1",
            is_paid=False,
        )
        self.client.login(username=self.user.username, password="StrongPass123!")

        response = self.client.get(
            reverse("bookings:ticket_view", kwargs={"booking_id": booking.id})
        )

        self.assertRedirects(
            response, reverse("payments:checkout", kwargs={"booking_id": booking.id})
        )

    def test_paid_ticket_is_accessible(self):
        booking = Booking.objects.create(
            user=self.user,
            trip=self.future_trip,
            seats_booked=2,
            booking_reference="BKPAID001",
            is_paid=True,
        )
        self.client.login(username=self.user.username, password="StrongPass123!")

        response = self.client.get(
            reverse("bookings:ticket_view", kwargs={"booking_id": booking.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your ticket")
