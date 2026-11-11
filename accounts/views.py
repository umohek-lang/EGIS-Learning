
from urllib.parse import urlencode
from certificates.models import Certificate
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
    url_has_allowed_host_and_scheme,
)
from django.views.decorators.http import require_GET

from subscriptions.models import Subscription
from courses.models import Course

from .forms import StudentRegistrationForm
from .tokens import email_verification_token


User = get_user_model()


def get_safe_next_url(request, next_url=None):
    """
    Preserve a safe internal destination during authentication.
    Prevent external redirect attacks.
    """

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return ""


def register(request):

    next_url = get_safe_next_url(
        request,
        request.POST.get("next") or request.GET.get("next"),
    )

    if request.user.is_authenticated:
        return redirect(next_url or "dashboard")

    if request.method == "POST":

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.is_active = True
            user.email_verified = False

            user.save()

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = email_verification_token.make_token(user)

            verification_url = request.build_absolute_uri(
                reverse(
                    "verify_email",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    },
                )
            )

            if next_url:
                verification_url += "?" + urlencode({
                    "next": next_url
                })

            send_mail(
                subject="Verify your EGIS Learning email",
                message=(
                    f"Hello {user.first_name},\n\n"
                    "Thank you for registering with EGIS Learning.\n"
                    "Verify your email address using this link:\n\n"
                    f"{verification_url}\n\n"
                    "This link expires after 24 hours."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return render(
                request,
                "registration/verification_sent.html",
                {
                    "email": user.email,
                    "next": next_url,
                },
            )

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@require_GET
def verify_email(request, uidb64, token):

    next_url = get_safe_next_url(
        request,
        request.GET.get("next"),
    )

    try:

        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        user = User.objects.get(pk=uid)

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):

        user = None

    if user is None:

        messages.error(
            request,
            "This verification link is invalid.",
        )

        return redirect("login")

    if user.email_verified:

        messages.info(
            request,
            "Your email has already been verified.",
        )

        login_url = reverse("login")

        if next_url:
            login_url += "?" + urlencode({
                "next": next_url
            })

        return redirect(login_url)

    if email_verification_token.check_token(user, token):

        user.email_verified = True

        user.save(
            update_fields=["email_verified"]
        )

        messages.success(
            request,
            "Your email has been verified. You can now log in.",
        )

        login_url = reverse("login")

        if next_url:
            login_url += "?" + urlencode({
                "next": next_url
            })

        return redirect(login_url)

    messages.error(
        request,
        "This verification link is invalid or has expired. "
        "Please request a new one.",
    )

    resend_url = reverse("resend_verification")

    if next_url:
        resend_url += "?" + urlencode({
            "next": next_url
        })

    return redirect(resend_url)


def resend_verification(request):

    next_url = get_safe_next_url(
        request,
        request.POST.get("next") or request.GET.get("next"),
    )

    if request.method == "POST":

        email = request.POST.get(
            "email",
            "",
        ).strip()

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if user and not user.email_verified:

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = email_verification_token.make_token(user)

            verification_url = request.build_absolute_uri(
                reverse(
                    "verify_email",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    },
                )
            )

            if next_url:
                verification_url += "?" + urlencode({
                    "next": next_url
                })

            send_mail(
                "Verify your EGIS Learning email",
                (
                    "Verify your email using this link:\n\n"
                    f"{verification_url}\n\n"
                    "This link expires after 24 hours."
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        return render(
            request,
            "registration/resend_sent.html",
            {
                "next": next_url,
            },
        )

    return render(
        request,
        "registration/resend_verification.html",
        {
            "next": next_url,
        },
    )


@login_required
def dashboard(request):

    now = timezone.now()

    # Get the student's active subscriptions
    active_subscriptions = Subscription.objects.filter(
        user=request.user,
        status=Subscription.Status.ACTIVE,
        starts_at__lte=now,
        ends_at__gt=now,
    ).select_related(
        "plan",
        "plan__course",
        "plan__course__category",
    )

    # Get published courses
    courses = Course.objects.filter(
        is_published=True,
        category__is_active=True,
    ).select_related(
        "category",
    )

    # Get certificates belonging to the logged-in student
    certificates = Certificate.objects.filter(
        user=request.user,
    ).select_related(
        "course",
    ).order_by(
        "-issued_at",
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "active_subscriptions": active_subscriptions,
            "courses": courses,
            "certificates": certificates,
        },
    )