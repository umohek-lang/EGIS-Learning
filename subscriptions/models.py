from django.conf import settings
from django.db import models
from django.utils import timezone

from courses.models import Course


class SubscriptionPlan(models.Model):

    name = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="subscription_plans",
        null=True,
    )

    duration_months = models.PositiveSmallIntegerField(
        choices=[
            (i, f"{i} month{'s' if i > 1 else ''}")
            for i in range(1, 7)
        ],
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="NGN",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["duration_months"]

        constraints = [
            models.UniqueConstraint(
                fields=["course", "duration_months"],
                name="unique_course_subscription_duration",
            )
        ]

    def __str__(self):
        return (
            f"{self.course.title if self.course else 'Unassigned'} - "
            f"{self.name} - {self.currency} {self.price}"
        )


class Subscription(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    starts_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    ends_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_currently_active(self):
        now = timezone.now()

        return (
            self.status == self.Status.ACTIVE
            and self.starts_at is not None
            and self.ends_at is not None
            and self.starts_at <= now < self.ends_at
        )

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"