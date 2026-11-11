from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        INSTRUCTOR = "instructor", "Instructor"
        ADMINISTRATOR = "administrator", "Administrator"
        CONTENT_MANAGER = "content_manager", "Content Manager"
        SUPPORT_AGENT = "support_agent", "Support Agent"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
