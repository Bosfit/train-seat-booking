from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def roll_forward_past_trips(apps, schema_editor):
    TrainTrip = apps.get_model("bookings", "TrainTrip")
    now = timezone.now()
    future_start = now + timedelta(days=1)

    past_trips = TrainTrip.objects.filter(departure_time__lte=now).order_by("departure_time")

    for index, trip in enumerate(past_trips):
        # Keep seed/demo trips usable by moving old departures into the future.
        trip.departure_time = future_start + timedelta(days=index, hours=2)
        trip.save(update_fields=["departure_time"])


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0002_seed_train_trips"),
    ]

    operations = [
        migrations.RunPython(roll_forward_past_trips, migrations.RunPython.noop),
    ]
