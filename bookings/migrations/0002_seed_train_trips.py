from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def seed_train_trips(apps, schema_editor):
    TrainTrip = apps.get_model("bookings", "TrainTrip")
    now = timezone.now()

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
    ]

    for trip in starter_trips:
        TrainTrip.objects.get_or_create(
            origin=trip["origin"],
            destination=trip["destination"],
            departure_time=trip["departure_time"],
            defaults={
                "price": trip["price"],
                "seats_available": trip["seats_available"],
            },
        )


def remove_seed_train_trips(apps, schema_editor):
    TrainTrip = apps.get_model("bookings", "TrainTrip")
    TrainTrip.objects.filter(
        origin__in=["London", "Birmingham", "Bristol"],
        destination__in=["Manchester", "Leeds", "Cardiff"],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_train_trips, remove_seed_train_trips),
    ]
