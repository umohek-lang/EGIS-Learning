import calendar
import uuid
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from subscriptions.models import Subscription, SubscriptionPlan

from .models import Payment


def add_months(start_date, months):
    """
    Add calendar months while handling month-end dates safely.
    """

    month_index = start_date.month - 1 + months

    year = start_date.year + month_index // 12
    month = month_index % 12 + 1

    day = min(
        start_date.day,
        calendar.monthrange(year, month)[1],
    )

    return start_date.replace(
        year=year,
        month=month,
        day=day,
    )


def course_redirect(course, show_plans=False):
    """
    Redirect the student to the appropriate course page.
    """

    if (
        course
        and course.is_published
        and course.category.is_active
    ):

        if show_plans:
            return redirect(
                "plans",
                course_slug=course.slug,
            )

        return redirect(
            "course_detail",
            slug=course.slug,
        )

    return redirect("training_list")


@login_required
def checkout(request, plan_id):

    if request.method != "POST":
        return redirect("training_list")

    plan = get_object_or_404(
        SubscriptionPlan.objects.select_related(
            "course",
            "course__category",
        ),
        pk=plan_id,
        is_active=True,
        course__isnull=False,
        course__is_published=True,
        course__category__is_active=True,
    )

    course = plan.course

    if not request.user.email_verified:
        messages.error(
            request,
            "Please verify your email address before making a payment.",
        )
        return redirect("resend_verification")

    secret_key = getattr(
        settings,
        "PAYSTACK_SECRET_KEY",
        "",
    )

    if (
        not secret_key
        or "REPLACE_WITH_YOUR" in secret_key
    ):
        messages.error(
            request,
            "Online payment is not configured yet. Please try again later.",
        )
        return course_redirect(course, show_plans=True)

    if plan.currency != "NGN":
        messages.error(
            request,
            "This checkout currently supports NGN plans only.",
        )
        return course_redirect(course, show_plans=True)

    if plan.price <= 0:
        messages.error(
            request,
            "This subscription plan has an invalid price.",
        )
        return course_redirect(course, show_plans=True)

    # Never trust a price submitted by the browser.
    amount_kobo = int(plan.price * 100)

    reference = "EGIS-" + uuid.uuid4().hex.upper()

    # Create a pending subscription.
    subscription = Subscription.objects.create(
        user=request.user,
        plan=plan,
        status=Subscription.Status.PENDING,
    )

    # Create a pending payment record.
    payment = Payment.objects.create(
        subscription=subscription,
        provider="paystack",
        reference=reference,
        amount=plan.price,
        currency=plan.currency,
        status=Payment.Status.PENDING,
    )

    callback_url = request.build_absolute_uri(
        reverse("payment_callback")
    )

    try:

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers={
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json",
            },
            json={
                "email": request.user.email,
                "amount": amount_kobo,
                "currency": plan.currency,
                "reference": payment.reference,
                "callback_url": callback_url,
                "metadata": {
                    "payment_reference": payment.reference,
                    "subscription_id": subscription.pk,
                    "user_id": request.user.pk,
                },
            },
            timeout=20,
        )

        response.raise_for_status()

        result = response.json()

    except (requests.RequestException, ValueError):

        messages.error(
            request,
            "We could not connect to Paystack. Please try again.",
        )

        return course_redirect(
            course,
            show_plans=True,
        )

    if (
        not result.get("status")
        or not result.get("data", {}).get("authorization_url")
    ):

        messages.error(
            request,
            "Paystack could not start your payment. Please try again.",
        )

        return course_redirect(
            course,
            show_plans=True,
        )

    # Redirect the student to Paystack checkout.
    return redirect(
        result["data"]["authorization_url"]
    )


@login_required
@require_GET
def payment_callback(request):

    reference = request.GET.get(
        "reference",
        "",
    ).strip()

    if not reference:

        messages.error(
            request,
            "No payment reference was received.",
        )

        return redirect("training_list")

    payment = get_object_or_404(
        Payment.objects.select_related(
            "subscription",
            "subscription__plan",
            "subscription__plan__course",
            "subscription__plan__course__category",
            "subscription__user",
        ),
        reference=reference,
        subscription__user=request.user,
    )

    subscription = payment.subscription
    course = subscription.plan.course

    # Prevent processing an already successful payment again.
    if payment.status == Payment.Status.SUCCESSFUL:

        messages.success(
            request,
            "Your payment has already been confirmed.",
        )

        return course_redirect(course)

    secret_key = getattr(
        settings,
        "PAYSTACK_SECRET_KEY",
        "",
    )

    if not secret_key:

        messages.error(
            request,
            "Payment verification is not configured.",
        )

        return course_redirect(
            course,
            show_plans=True,
        )

    try:

        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{payment.reference}",
            headers={
                "Authorization": f"Bearer {secret_key}",
            },
            timeout=20,
        )

        response.raise_for_status()

        result = response.json()

    except (requests.RequestException, ValueError):

        messages.error(
            request,
            "We could not verify your payment right now. Please try again.",
        )

        return course_redirect(
            course,
            show_plans=True,
        )

    data = result.get("data") or {}

    expected_amount_kobo = int(
        payment.amount * 100
    )

    # Verify the transaction directly with Paystack.
    valid_payment = (
        result.get("status") is True
        and data.get("status") == "success"
        and data.get("reference") == payment.reference
        and data.get("amount") == expected_amount_kobo
        and data.get("currency") == payment.currency
    )

    if not valid_payment:

        if data.get("status") in (
            "failed",
            "abandoned",
        ):

            payment.status = Payment.Status.FAILED

            payment.provider_response = data

            payment.save(
                update_fields=[
                    "status",
                    "provider_response",
                ]
            )

        messages.error(
            request,
            "Payment has not been confirmed. Your subscription remains inactive.",
        )

        return course_redirect(
            course,
            show_plans=True,
        )

    # Activate the subscription only after successful verification.
    with transaction.atomic():

        locked_payment = (
            Payment.objects
            .select_for_update()
            .select_related(
                "subscription",
                "subscription__plan",
            )
            .get(pk=payment.pk)
        )

        if locked_payment.status != Payment.Status.SUCCESSFUL:

            now = timezone.now()

            locked_subscription = locked_payment.subscription

            locked_subscription.status = Subscription.Status.ACTIVE

            locked_subscription.starts_at = now

            locked_subscription.ends_at = add_months(
                now,
                locked_subscription.plan.duration_months,
            )

            locked_subscription.save(
                update_fields=[
                    "status",
                    "starts_at",
                    "ends_at",
                ]
            )

            locked_payment.status = Payment.Status.SUCCESSFUL

            locked_payment.verified_at = now

            locked_payment.provider_response = data

            locked_payment.save(
                update_fields=[
                    "status",
                    "verified_at",
                    "provider_response",
                ]
            )

    messages.success(
        request,
        "Payment verified successfully. Your subscription is now active.",
    )

    return course_redirect(course)
