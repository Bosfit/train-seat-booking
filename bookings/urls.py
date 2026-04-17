from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.home, name="home"),
    path("book/<int:trip_id>/", views.create_booking, name="create_booking"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("my-bookings/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path("my-bookings/<int:booking_id>/edit/", views.update_booking, name="update_booking"),
    path("my-bookings/<int:booking_id>/delete/", views.delete_booking, name="delete_booking"),
]
