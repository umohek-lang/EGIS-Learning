import uuid

from django.db import transaction
from django.utils import timezone

from courses.models import Lesson, LessonProgress
from subscriptions.models import Subscription

from .models import Certificate, CertificateSettings


@transaction.atomic
def issue_certificate_if_eligible(user, course):
    """
    Automatically issue a certificate when a student
    successfully completes all required course lessons.
    """

    # 1. Confirm that the user is logged in.
    if not user.is_authenticated:
        return None

    # 2. Check whether a certificate already exists.
    existing_certificate = Certificate.objects.filter(
        user=user,
        course=course,
    ).first()

    if existing_certificate:
        return existing_certificate

    # 3. The course must be published and its category active.
    if not course.is_published or not course.category.is_active:
        return None

    # 4. Get all published lessons inside published modules.
    # Lessons without uploaded videos are excluded because
    # your existing course progress system does not count them.

    required_lessons = Lesson.objects.filter(
        module__course=course,
        module__is_published=True,
        is_published=True,
    ).exclude(
        video_file=""
    )

    total_lessons = required_lessons.count()

    # A course without required video lessons cannot
    # automatically qualify a student for a certificate.
    if total_lessons == 0:
        return None

    # 5. If the course contains paid lessons, check that
    # the student has an active subscription for this course.

    has_paid_lessons = required_lessons.filter(
        is_free_preview=False
    ).exists()

    if has_paid_lessons:

        now = timezone.now()

        subscription_active = Subscription.objects.filter(
            user=user,
            plan__course=course,
            status=Subscription.Status.ACTIVE,
            starts_at__lte=now,
            ends_at__gt=now,
        ).exists()

        if not subscription_active:
            return None

    # 6. Count the student's completed required lessons.

    completed_lessons = LessonProgress.objects.filter(
        user=user,
        lesson__in=required_lessons,
        is_completed=True,
    ).count()

    # Every required lesson must be completed.
    if completed_lessons != total_lessons:
        return None

    # 7. Load the certificate settings.
    # If the administrator has not configured them yet,
    # Django model defaults will be used.

    certificate_settings = (
        CertificateSettings.objects.first()
        or CertificateSettings()
    )

    # Respect the automatic issuance setting.
    if not certificate_settings.auto_issue:
        return None

    # 8. Get the student's display name.
    student_name = (
        user.get_full_name().strip()
        or user.username
        or user.email
    )

    # 9. Generate a unique certificate number.
    prefix = (
        certificate_settings.certificate_prefix
        or "EGIS"
    )

    certificate_number = (
        f"{prefix}-{timezone.now().year}-"
        f"{uuid.uuid4().hex[:10].upper()}"
    )

    # 10. Save the certificate and preserve the current
    # certificate design information as snapshots.

    certificate, created = Certificate.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            "certificate_number": certificate_number,

            "student_name": student_name,
            "course_title": course.title,

            "institution_name": (
                certificate_settings.institution_name
            ),

            "certificate_title": (
                certificate_settings.certificate_title
            ),

            "description": (
                certificate_settings.description
            ),

            "signatory_name": (
                certificate_settings.signatory_name
            ),

            "signatory_position": (
                certificate_settings.signatory_position
            ),

            "footer_text": (
                certificate_settings.footer_text
            ),

            "institution_logo_snapshot": (
                certificate_settings.institution_logo.name
                if certificate_settings.institution_logo
                else ""
            ),

            "signature_snapshot": (
                certificate_settings.signature_image.name
                if certificate_settings.signature_image
                else ""
            ),

            "background_snapshot": (
                certificate_settings.certificate_background.name
                if certificate_settings.certificate_background
                else ""
            ),
        },
    )

    return certificate