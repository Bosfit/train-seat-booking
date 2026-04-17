from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.home, name="home"),
    path("book/<int:trip_id>/", views.create_booking, name="create_booking"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
]
