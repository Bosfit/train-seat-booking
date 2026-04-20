from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/<int:booking_id>/", views.checkout, name="checkout"),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
]
