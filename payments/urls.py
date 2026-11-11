from django.urls import path

from . import views

urlpatterns = [
    path(
        "checkout/<int:plan_id>/",
        views.checkout,
        name="payment_checkout",
    ),
    path(
        "callback/",
        views.payment_callback,
        name="payment_callback",
    ),
]
