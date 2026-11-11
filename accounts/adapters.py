from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


User = get_user_model()


class EGISSocialAccountAdapter(DefaultSocialAccountAdapter):

    """
    Custom Google authentication adapter for EGIS Learning.

    Supports:
    - New Google student registration.
    - Existing account authentication through verified Google email.
    - Automatic connection of matching Google accounts.
    - Protection against unverified Google emails.
    - Protection against unauthorized account linking.
    """

    def populate_user(self, request, sociallogin, data):

        user = super().populate_user(request, sociallogin, data)

        # New Google registrations receive the student role.
        user.role = User.Role.STUDENT

        extra_data = sociallogin.account.extra_data

        # Only trust Google's verified email status.
        user.email_verified = (
            extra_data.get("email_verified") is True
        )

        return user

    def pre_social_login(self, request, sociallogin):

        # Only apply these checks to Google authentication.
        if sociallogin.account.provider != "google":
            return super().pre_social_login(request, sociallogin)

        extra_data = sociallogin.account.extra_data

        google_email = (
            extra_data.get("email")
            or sociallogin.user.email
            or ""
        )

        google_verified = (
            extra_data.get("email_verified") is True
        )

        # Reject missing or unverified Google email addresses.
        if not google_email or not google_verified:

            raise ImmediateHttpResponse(
                HttpResponseForbidden(
                    "Google could not verify your email address. "
                    "Please verify your Google email before continuing."
                )
            )

        google_email = google_email.strip().lower()

        # Allow an already connected Google account.
        if sociallogin.is_existing:
            return super().pre_social_login(request, sociallogin)

        # When an authenticated user explicitly connects Google,
        # the Google email must match their existing EGIS email.
        if request.user.is_authenticated:

            existing_email = (
                request.user.email or ""
            ).strip().lower()

            if existing_email != google_email:

                raise ImmediateHttpResponse(
                    HttpResponseForbidden(
                        "Your Google email must match your "
                        "EGIS account email before connecting."
                    )
                )

        # IMPORTANT:
        # Do not reject an existing email here.
        #
        # Django Allauth handles matching verified email addresses
        # through SOCIALACCOUNT_EMAIL_AUTHENTICATION.
        #
        # SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT
        # automatically connects the Google account to the
        # existing EGIS account.

        return super().pre_social_login(request, sociallogin)

    def save_user(self, request, sociallogin, form=None):

        user = super().save_user(
            request,
            sociallogin,
            form=form
        )

        extra_data = sociallogin.account.extra_data

        user.email_verified = (
            extra_data.get("email_verified") is True
        )

        # New Google registrations are students by default.
        user.role = User.Role.STUDENT

        user.save(
            update_fields=[
                "email_verified",
                "role",
            ]
        )

        return user