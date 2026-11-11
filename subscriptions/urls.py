from django.urls import path
from . import views


urlpatterns = [
    path(
        "course/<slug:course_slug>/",
        views.plan_list,
        name="plans",
    ),
]