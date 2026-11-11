from django.contrib import admin
from .models import SubscriptionPlan, Subscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
    "name",
    "course",
    "duration_months",
    "price",
    "currency",
    "is_active",
        )

           
    list_filter = (
    "course",
    "duration_months",
    "is_active",
    "currency",
    )

    search_fields = (
    "name",
    "course__title",
    )

    autocomplete_fields = ("course",)
    

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
    "user",
    "plan",
    "status",
    "starts_at",
    "ends_at",
    "created_at",
    )

  
    list_filter = (
    "status",
    "plan__course",
    )

    search_fields = (
    "user__email",
    "plan__name",
    "plan__course__title",
    )

    readonly_fields = ("created_at",)
   

