from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import Certificate
from .pdf_generator import generate_certificate_pdf


# ======================================================
# SECURE STUDENT CERTIFICATE DOWNLOAD
# ======================================================

@login_required
@require_GET
def download_certificate(request, certificate_id):

    # --------------------------------------------------
    # 1. Find certificate belonging to logged-in student
    # --------------------------------------------------

    certificate = get_object_or_404(
        Certificate,
        pk=certificate_id,
        user=request.user,
        status=Certificate.Status.ISSUED,
    )

    # --------------------------------------------------
    # 2. Check whether PDF already exists
    # --------------------------------------------------

    pdf_exists = False

    if certificate.pdf_file:
        try:
            pdf_exists = certificate.pdf_file.storage.exists(
                certificate.pdf_file.name
            )
        except Exception:
            pdf_exists = False

    # --------------------------------------------------
    # 3. Generate PDF if it does not exist
    # --------------------------------------------------

    if not pdf_exists:

        verification_url = request.build_absolute_uri(
            reverse(
                "certificate_verify",
                kwargs={
                    "certificate_number": certificate.certificate_number
                },
            )
        )

        pdf_content = generate_certificate_pdf(
            certificate,
            verification_url,
        )

        filename = (
            f"{certificate.certificate_number}.pdf"
        )

        certificate.pdf_file.save(
            filename,
            ContentFile(pdf_content),
            save=True,
        )

    # --------------------------------------------------
    # 4. Return PDF as secure download
    # --------------------------------------------------

    response = FileResponse(
        certificate.pdf_file.open("rb"),
        as_attachment=True,
        filename=f"{certificate.certificate_number}.pdf",
        content_type="application/pdf",
    )

    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"

    return response


# ======================================================
# PUBLIC CERTIFICATE VERIFICATION
# ======================================================

@require_GET
def verify_certificate(request, certificate_number):

    # --------------------------------------------------
    # 1. Find certificate using certificate number
    # --------------------------------------------------

    certificate = get_object_or_404(
        Certificate,
        certificate_number=certificate_number,
    )

    # --------------------------------------------------
    # 2. Determine certificate validity
    # --------------------------------------------------

    is_valid = (
        certificate.status == Certificate.Status.ISSUED
    )

    # --------------------------------------------------
    # 3. Format issuance date
    # --------------------------------------------------

    issued_date = timezone.localtime(
        certificate.issued_at
    ).strftime("%d %B %Y")

    # --------------------------------------------------
    # 4. Format revocation date if applicable
    # --------------------------------------------------

    revoked_date = None

    if certificate.revoked_at:

        revoked_date = timezone.localtime(
            certificate.revoked_at
        ).strftime("%d %B %Y")

    # --------------------------------------------------
    # 5. Prepare verification information
    # --------------------------------------------------

    context = {
        "certificate": certificate,

        "is_valid": is_valid,

        "status_label": (
            "VALID CERTIFICATE"
            if is_valid
            else "REVOKED CERTIFICATE"
        ),

        "issued_date": issued_date,

        "revoked_date": revoked_date,
    }

    # --------------------------------------------------
    # 6. Display professional verification webpage
    # --------------------------------------------------

    response = render(
        request,
        "certificates/verify_certificate.html",
        context,
    )

    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"

    return response