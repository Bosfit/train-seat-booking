from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def roll_forward_past_trips(apps, schema_editor):
    TrainTrip = apps.get_model("bookings", "TrainTrip")
    now = timezone.now()
    future_start = now + timedelta(days=1)

    past_trips = TrainTrip.objects.filter(departure_time__lte=now).order_by(
        "departure_time"
    )

    for index, trip in enumerate(past_trips):
        trip.departure_time = future_start + timedelta(days=index, hours=2)
        trip.save(update_fields=["departure_time"])

    # Extra future trips so the live site stays bookable for assessment.
    extra_trips = [
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
        {
            "origin": "London",
            "destination": "Brighton",
            "departure_time": now + timedelta(days=6, hours=1),
            "price": "19.00",
            "seats_available": 100,
        },
    ]

    for trip in extra_trips:
        TrainTrip.objects.get_or_create(
            origin=trip["origin"],
            destination=trip["destination"],
            departure_time=trip["departure_time"],
            defaults={
                "price": trip["price"],
                "seats_available": trip["seats_available"],
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0003_roll_forward_past_trips"),
    ]

    operations = [
        migrations.RunPython(roll_forward_past_trips, migrations.RunPython.noop),
    ]
