import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from bookings.models import Booking


@login_required(login_url="accounts:login")
def checkout(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("trip"),
        id=booking_id,
        user=request.user,
    )

    if booking.is_paid:
        messages.info(request, "This booking is already paid.")
        return redirect("bookings:booking_detail", booking_id=booking.id)

    if request.method == "POST":
        if not settings.STRIPE_SECRET_KEY:
            messages.error(request, "Stripe is not configured yet. Add STRIPE keys in your env.")
            return redirect("bookings:booking_detail", booking_id=booking.id)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "unit_amount": int(booking.trip.price * 100),
                        "product_data": {
                            "name": f"{booking.trip.origin} to {booking.trip.destination}",
                            "description": f"{booking.seats_booked} seat(s)",
                        },
                    },
                    "quantity": booking.seats_booked,
                }
            ],
            metadata={
                "booking_id": str(booking.id),
                "user_id": str(request.user.id),
            },
            success_url=(
                request.build_absolute_uri(reverse("payments:success"))
                + f"?booking_id={booking.id}&session_id={{CHECKOUT_SESSION_ID}}"
            ),
            cancel_url=request.build_absolute_uri(
                reverse("payments:cancel") + f"?booking_id={booking.id}"
            ),
        )
        return redirect(session.url, permanent=False)

    total_price = booking.trip.price * booking.seats_booked
    return render(
        request,
        "payments/checkout.html",
        {"booking": booking, "total_price": total_price},
    )


@login_required(login_url="accounts:login")
def success(request):
    booking = get_object_or_404(
        Booking.objects.select_related("trip"),
        id=request.GET.get("booking_id"),
        user=request.user,
    )
    session_id = request.GET.get("session_id")

    if booking.is_paid:
        messages.info(request, "This booking was already marked as paid.")
        return redirect("bookings:booking_detail", booking_id=booking.id)

    if not settings.STRIPE_SECRET_KEY or not session_id:
        messages.error(request, "Could not confirm payment.")
        return redirect("bookings:booking_detail", booking_id=booking.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        messages.error(request, "Could not confirm payment with Stripe.")
        return redirect("bookings:booking_detail", booking_id=booking.id)

    if session.payment_status == "paid":
        booking.is_paid = True
        booking.save(update_fields=["is_paid"])
        messages.success(request, "Payment successful. Your booking is now paid.")
    else:
        messages.warning(request, "Payment is not confirmed yet.")

    return render(request, "payments/success.html", {"booking": booking})


@login_required(login_url="accounts:login")
def cancel(request):
    booking = get_object_or_404(
        Booking,
        id=request.GET.get("booking_id"),
        user=request.user,
    )
    messages.info(request, "Payment was cancelled. Your booking is still unpaid.")
    return render(request, "payments/cancel.html", {"booking": booking})
