from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, TrainTrip


@override_settings(STRIPE_SECRET_KEY="sk_test_123")
class PaymentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="payer", password="StrongPass123!")
        self.other_user = User.objects.create_user(username="other", password="StrongPass123!")
        self.trip = TrainTrip.objects.create(
            origin="Cardiff",
            destination="London",
            departure_time=timezone.now() + timedelta(days=2),
            price="25.00",
            seats_available=20,
        )
        self.booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            seats_booked=2,
            booking_reference="BKPAY001",
            is_paid=False,
        )

    @patch("payments.views.stripe.checkout.Session.create")
    def test_checkout_post_redirects_to_stripe_session_url(self, mock_create):
        mock_create.return_value = SimpleNamespace(url="https://stripe.example/checkout")
        self.client.login(username=self.user.username, password="StrongPass123!")

        response = self.client.post(
            reverse("payments:checkout", kwargs={"booking_id": self.booking.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://stripe.example/checkout")

    def test_paid_booking_cannot_checkout_again(self):
        self.booking.is_paid = True
        self.booking.save(update_fields=["is_paid"])
        self.client.login(username=self.user.username, password="StrongPass123!")

        response = self.client.get(
            reverse("payments:checkout", kwargs={"booking_id": self.booking.id})
        )

        self.assertRedirects(
            response,
            reverse("bookings:booking_detail", kwargs={"booking_id": self.booking.id}),
        )

    @patch("payments.views.stripe.checkout.Session.retrieve")
    def test_success_marks_booking_paid(self, mock_retrieve):
        mock_retrieve.return_value = SimpleNamespace(payment_status="paid")
        self.client.login(username=self.user.username, password="StrongPass123!")

        response = self.client.get(
            reverse("payments:success"),
            {"booking_id": self.booking.id, "session_id": "cs_test_123"},
        )

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.is_paid)

    def test_user_cannot_access_other_users_checkout(self):
        self.client.login(username=self.other_user.username, password="StrongPass123!")

        response = self.client.get(
            reverse("payments:checkout", kwargs={"booking_id": self.booking.id})
        )

        self.assertEqual(response.status_code, 404)
