from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import TrainTrip


class Command(BaseCommand):
    help = "Move past trips into the future and ensure starter routes exist."

    def handle(self, *args, **options):
        now = timezone.now()
        future_start = now + timedelta(days=1)

        past_trips = TrainTrip.objects.filter(departure_time__lte=now).order_by(
            "departure_time"
        )
        updated = 0
        for index, trip in enumerate(past_trips):
            trip.departure_time = future_start + timedelta(days=index, hours=2)
            trip.save(update_fields=["departure_time"])
            updated += 1

        starter_trips = [
            {
                "origin": "London",
                "destination": "Manchester",
                "departure_time": now + timedelta(days=2, hours=2),
                "price": "45.00",
                "seats_available": 120,
            },
            {
                "origin": "Birmingham",
                "destination": "Leeds",
                "departure_time": now + timedelta(days=3, hours=1),
                "price": "32.50",
                "seats_available": 80,
            },
            {
                "origin": "Bristol",
                "destination": "Cardiff",
                "departure_time": now + timedelta(days=1, hours=4),
                "price": "18.00",
                "seats_available": 60,
            },
            {
                "origin": "Edinburgh",
                "destination": "Glasgow",
                "departure_time": now + timedelta(days=4, hours=3),
                "price": "22.00",
                "seats_available": 90,
            },
            {
                "origin": "Liverpool",
                "destination": "York",
                "departure_time": now + timedelta(days=5, hours=2),
                "price": "28.50",
                "seats_available": 70,
            },
        ]

        created = 0
        for trip_data in starter_trips:
            _, was_created = TrainTrip.objects.get_or_create(
                origin=trip_data["origin"],
                destination=trip_data["destination"],
                departure_time=trip_data["departure_time"],
                defaults={
                    "price": trip_data["price"],
                    "seats_available": trip_data["seats_available"],
                },
            )
            if was_created:
                created += 1

        future_count = TrainTrip.objects.filter(departure_time__gt=now).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} past trip(s), created {created} new trip(s). "
                f"{future_count} bookable trip(s) now available."
            )
        )
