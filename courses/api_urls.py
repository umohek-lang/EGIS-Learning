from django.urls import path

from . import api_views


urlpatterns = [

    path(
        "homepage/",
        api_views.homepage_api,
        name="homepage_api"
    ),

]