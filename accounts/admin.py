
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "email_verified",
        "is_active",
    )

    list_filter = (
        "role",
        "email_verified",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "E-Learning Profile",
            {
                "fields": (
                    "role",
                    "email_verified",
                    "profile_picture",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "E-Learning Profile",
            {
                "fields": (
                    "email",
                    "role",
                    "email_verified",
                    "profile_picture",
                )
            },
        ),
    )
