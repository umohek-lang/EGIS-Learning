from django.conf import settings
from django.db import models
from .storage import PrivateCertificateStorage
from courses.models import Course


class CertificateSettings(models.Model):
    """
    Stores the certificate design and institutional
    information configured by the administrator.

    Only one settings record is allowed.
    """

    institution_name = models.CharField(
        max_length=200,
        default="Excellent Grade International School",
    )

    institution_logo = models.ImageField(
        upload_to="certificates/settings/",
        blank=True,
        null=True,
    )

    certificate_title = models.CharField(
        max_length=200,
        default="CERTIFICATE OF COMPLETION",
    )

    certificate_background = models.ImageField(
        upload_to="certificates/settings/",
        blank=True,
        null=True,
    )

    description = models.TextField(
        default=(
            "This is to certify that the student named "
            "below has successfully completed the course."
        ),
    )

    signatory_name = models.CharField(
        max_length=200,
        blank=True,
    )

    signatory_position = models.CharField(
        max_length=200,
        blank=True,
    )

    signature_image = models.ImageField(
        upload_to="certificates/settings/signatures/",
        blank=True,
        null=True,
    )

    footer_text = models.CharField(
        max_length=500,
        blank=True,
    )

    certificate_prefix = models.CharField(
        max_length=30,
        default="EGIS",
    )

    auto_issue = models.BooleanField(
        default=True,
        help_text=(
            "Automatically issue certificates when students "
            "satisfy the course completion requirements."
        ),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Certificate Settings"
        verbose_name_plural = "Certificate Settings"

    def save(self, *args, **kwargs):
        # Keep a single certificate settings record.
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "EGIS Certificate Settings"


class Certificate(models.Model):
    """
    Stores certificates issued to students.
    """

    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        REVOKED = "revoked", "Revoked"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="certificates",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="certificates",
    )

    certificate_number = models.CharField(
        max_length=100,
        unique=True,
    )

    issued_at = models.DateTimeField(
        auto_now_add=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ISSUED,
    )

    revoked_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    revocation_reason = models.TextField(
        blank=True,
    )

    # Preserve certificate information at the time of issuance.

    student_name = models.CharField(
        max_length=200,
    )

    course_title = models.CharField(
        max_length=200,
    )

    institution_name = models.CharField(
        max_length=200,
    )

    certificate_title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    signatory_name = models.CharField(
        max_length=200,
        blank=True,
    )

    signatory_position = models.CharField(
        max_length=200,
        blank=True,
    )

    footer_text = models.CharField(
        max_length=500,
        blank=True,
    )

    # Preserve the image paths used when the certificate was issued.

    institution_logo_snapshot = models.CharField(
        max_length=500,
        blank=True,
    )

    signature_snapshot = models.CharField(
        max_length=500,
        blank=True,
    )

    background_snapshot = models.CharField(
        max_length=500,
        blank=True,
    )
    # Securely stored generated certificate PDF.

    pdf_file = models.FileField(
        storage=PrivateCertificateStorage(),
        upload_to="certificates/generated/",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-issued_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_certificate_per_student_course",
            )
        ]

    def __str__(self):
        return (
            f"{self.certificate_number} - "
            f"{self.student_name} - {self.course_title}"
        )