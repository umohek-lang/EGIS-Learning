from django import forms
from django.contrib import admin

from .models import SubscriptionPlan, Subscription


class SubscriptionPlanForm(forms.ModelForm):

    class Meta:
        model = SubscriptionPlan
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A new subscription plan must belong to a course.
        self.fields["course"].required = True


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):

    form = SubscriptionPlanForm

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

    ordering = ("course", "duration_months")


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
        "plan",
    )

    search_fields = (
        "user__email",
        "plan__name",
        "plan__course__title",
    )

    readonly_fields = ("created_at",)