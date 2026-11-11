
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "subscription",
        "amount",
        "currency",
        "status",
        "verified_at",
        "created_at",
    )
    list_filter = ("status", "provider", "currency")
    search_fields = (
        "reference",
        "subscription__user__email",
    )
    readonly_fields = (
        "reference",
        "amount",
        "currency",
        "status",
        "verified_at",
        "provider_response",
        "created_at",
    )
