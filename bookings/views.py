from django.shortcuts import render


def home(request):
    """Site home page — uses templates/bookings/home.html which extends base.html."""
    return render(request, "bookings/home.html")
