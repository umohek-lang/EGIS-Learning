
from django.db import models
from django.utils import timezone
from subscriptions.models import Subscription


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESSFUL = "successful", "Successful"
        FAILED = "failed", "Failed"

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    provider = models.CharField(max_length=30, default="paystack")
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    provider_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_successful(self, response=None):
        self.status = self.Status.SUCCESSFUL
        self.verified_at = timezone.now()
        if response is not None:
            self.provider_response = response
        self.save(
            update_fields=[
                "status",
                "verified_at",
                "provider_response",
            ]
        )

    def __str__(self):
        return f"{self.reference} - {self.status}"
