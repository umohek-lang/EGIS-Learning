from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

       # Redirect Django homepage to React frontend
    re_path(
        r'^$',
        RedirectView.as_view(
            url='http://localhost:5173/',
            permanent=False
        ),
        name='frontend_home'
    ),

     # Django admin
    path("admin/", admin.site.urls),

     # Accounts
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    
    # Subscriptions
    path("subscriptions/", include("subscriptions.urls")),
    
    # Payments
    path("payments/", include("payments.urls")),
    path("", include("courses.urls")),
    path("certificates/", include("certificates.urls")),
    path("api/", include("courses.api_urls")),
    path("learning/", include("learning.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
