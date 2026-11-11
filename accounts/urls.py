
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import VerifiedEmailAuthenticationForm


urlpatterns = [
    # Student registration
    path(
        "register/",
        views.register,
        name="register",
    ),

    # Login: require email verification
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=VerifiedEmailAuthenticationForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    # Logout
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # Student dashboard
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    # Verify email using the link sent to the student's email
    path(
        "verify-email/<uidb64>/<token>/",
        views.verify_email,
        name="verify_email",
    ),

    # Request another verification email
    path(
        "resend-verification/",
        views.resend_verification,
        name="resend_verification",
    ),
]
