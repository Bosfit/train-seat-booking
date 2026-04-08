from django.http import HttpResponse


def index(request):
    return HttpResponse("Bookings app is ready.")
