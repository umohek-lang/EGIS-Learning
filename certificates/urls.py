from django.urls import path

from . import views


urlpatterns = [

    # Secure student certificate download
    path(
        "<int:certificate_id>/download/",
        views.download_certificate,
        name="certificate_download",
    ),

    # Public certificate verification
    path(
        "verify/<str:certificate_number>/",
        views.verify_certificate,
        name="certificate_verify",
    ),

]