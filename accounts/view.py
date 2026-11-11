from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_GET

from courses.models import Course
from subscriptions.models import Subscription
from .forms import StudentRegistrationForm
from .tokens import email_verification_token

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
    
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.email_verified = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            verification_url = request.build_absolute_uri(
                reverse(
                    "verify_email",
                    kwargs={"uidb64": uid, "token": token},
                )
            )

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
                {"email": user.email},
            )
    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


@require_GET
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None:
        messages.error(request, "This verification link is invalid.")
        return redirect("login")

    if user.email_verified:
        messages.info(request, "Your email has already been verified.")
        return redirect("login")

    if email_verification_token.check_token(user, token):
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        messages.success(
            request,
            "Your email has been verified. You can now log in.",
        )
        return redirect("login")

    messages.error(
        request,
        "This verification link is invalid or has expired. Please request a new one.",
    )
    return redirect("resend_verification")


def resend_verification(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        user = User.objects.filter(email__iexact=email).first()

        # Keep the response generic to avoid revealing account existence.
        if user and not user.email_verified:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            verification_url = request.build_absolute_uri(
                reverse(
                    "verify_email",
                    kwargs={"uidb64": uid, "token": token},
                )
            )
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
        )

    return render(request, "registration/resend_verification.html")


@login_required
def dashboard(request):

    now = timezone.now()

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

    courses = Course.objects.filter(
        is_published=True,
        category__is_active=True,
    ).select_related(
        "category",
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "active_subscriptions": active_subscriptions,
            "courses": courses,
        },
    )