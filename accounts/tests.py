from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountViewsTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("bookings:home"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_with_next_redirects_to_requested_page(self):
        user = User.objects.create_user(username="anna", password="StrongPass123!")

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": user.username,
                "password": "StrongPass123!",
                "next": reverse("bookings:my_bookings"),
            },
        )

        self.assertRedirects(response, reverse("bookings:my_bookings"))

    def test_logout_redirects_home(self):
        user = User.objects.create_user(username="sam", password="StrongPass123!")
        self.client.login(username=user.username, password="StrongPass123!")

        response = self.client.get(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("bookings:home"))
