from django import forms

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["seats_booked"]
        widgets = {
            "seats_booked": forms.NumberInput(attrs={"min": 1}),
        }
