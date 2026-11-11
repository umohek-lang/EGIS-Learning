from io import BytesIO

from django.core.files.storage import default_storage
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas


def load_certificate_image(image_path):
    """
    Load an image from Django's default media storage.

    Returns None if the image is missing or cannot be opened.
    """

    if not image_path:
        return None

    try:
        with default_storage.open(image_path, "rb") as image_file:
            image_data = image_file.read()

        return ImageReader(BytesIO(image_data))

    except Exception:
        return None


def generate_certificate_pdf(certificate, verification_url):
    """
    Generate a professional A4 landscape certificate.

    Returns:
        PDF document as bytes.
    """

    buffer = BytesIO()

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        buffer,
        pagesize=landscape(A4),
    )

    # --------------------------------------------------
    # 1. CERTIFICATE BACKGROUND
    # --------------------------------------------------

    background = load_certificate_image(
        certificate.background_snapshot
    )

    if background:
        pdf.drawImage(
            background,
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=False,
            mask="auto",
        )
    else:
        pdf.setFillColor(colors.HexColor("#F8FBFF"))
        pdf.rect(
            0,
            0,
            page_width,
            page_height,
            fill=1,
            stroke=0,
        )

    # --------------------------------------------------
    # 2. DECORATIVE BORDERS
    # --------------------------------------------------

    pdf.setStrokeColor(colors.HexColor("#163B65"))
    pdf.setLineWidth(4)

    pdf.rect(
        22,
        22,
        page_width - 44,
        page_height - 44,
        fill=0,
        stroke=1,
    )

    pdf.setStrokeColor(colors.HexColor("#C9A227"))
    pdf.setLineWidth(1.5)

    pdf.rect(
        30,
        30,
        page_width - 60,
        page_height - 60,
        fill=0,
        stroke=1,
    )

    # --------------------------------------------------
    # 3. INSTITUTION LOGO
    # --------------------------------------------------

    logo = load_certificate_image(
        certificate.institution_logo_snapshot
    )

    if logo:
        pdf.drawImage(
            logo,
            55,
            page_height - 125,
            width=85,
            height=75,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )

    # --------------------------------------------------
    # 4. INSTITUTION NAME
    # --------------------------------------------------

    pdf.setFillColor(colors.HexColor("#163B65"))

    pdf.setFont("Helvetica-Bold", 20)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 75,
        certificate.institution_name.upper(),
    )

    # --------------------------------------------------
    # 5. CERTIFICATE TITLE
    # --------------------------------------------------

    pdf.setFillColor(colors.HexColor("#B08A20"))

    pdf.setFont("Helvetica-Bold", 24)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 145,
        certificate.certificate_title.upper(),
    )

    # Decorative line

    pdf.setStrokeColor(colors.HexColor("#C9A227"))
    pdf.setLineWidth(2)

    pdf.line(
        170,
        page_height - 160,
        page_width - 170,
        page_height - 160,
    )

    # --------------------------------------------------
    # 6. CERTIFICATE DESCRIPTION
    # --------------------------------------------------

    pdf.setFillColor(colors.HexColor("#333333"))
    pdf.setFont("Helvetica", 12)

    description = certificate.description or (
        "This is to certify that the student named below "
        "has successfully completed the course."
    )

    description_lines = simpleSplit(
        description,
        "Helvetica",
        12,
        page_width - 180,
    )

    description_y = page_height - 200

    for line in description_lines[:3]:
        pdf.drawCentredString(
            page_width / 2,
            description_y,
            line,
        )

        description_y -= 18

    # --------------------------------------------------
    # 7. STUDENT NAME
    # --------------------------------------------------

    student_y = description_y - 35

    pdf.setFillColor(colors.HexColor("#163B65"))
    pdf.setFont("Helvetica-Bold", 27)

    pdf.drawCentredString(
        page_width / 2,
        student_y,
        certificate.student_name.upper(),
    )

    # Student name underline

    pdf.setStrokeColor(colors.HexColor("#C9A227"))
    pdf.setLineWidth(1)

    pdf.line(
        170,
        student_y - 12,
        page_width - 170,
        student_y - 12,
    )

    # --------------------------------------------------
    # 8. COURSE TITLE
    # --------------------------------------------------

    course_y = student_y - 45

    pdf.setFillColor(colors.HexColor("#333333"))
    pdf.setFont("Helvetica", 12)

    pdf.drawCentredString(
        page_width / 2,
        course_y,
        "For successfully completing the course:",
    )

    pdf.setFillColor(colors.HexColor("#163B65"))
    pdf.setFont("Helvetica-Bold", 18)

    course_lines = simpleSplit(
        certificate.course_title,
        "Helvetica-Bold",
        18,
        page_width - 180,
    )

    course_y -= 27

    for line in course_lines[:2]:
        pdf.drawCentredString(
            page_width / 2,
            course_y,
            line,
        )

        course_y -= 23

    # --------------------------------------------------
    # 9. DATE OF ISSUANCE
    # --------------------------------------------------

    issued_date = timezone.localtime(
        certificate.issued_at
    ).strftime("%d %B %Y")

    pdf.setFillColor(colors.HexColor("#444444"))
    pdf.setFont("Helvetica", 11)

    pdf.drawCentredString(
        page_width / 2,
        105,
        f"Date of Issue: {issued_date}",
    )

    # --------------------------------------------------
    # 10. SIGNATURE
    # --------------------------------------------------

    signature = load_certificate_image(
        certificate.signature_snapshot
    )

    signature_x = page_width - 205
    signature_y = 65

    if signature:
        pdf.drawImage(
            signature,
            signature_x,
            signature_y + 12,
            width=115,
            height=45,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )

    pdf.setStrokeColor(colors.HexColor("#333333"))
    pdf.setLineWidth(0.8)

    pdf.line(
        signature_x - 5,
        signature_y + 8,
        signature_x + 120,
        signature_y + 8,
    )

    pdf.setFillColor(colors.HexColor("#163B65"))
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawCentredString(
        signature_x + 57,
        signature_y - 8,
        certificate.signatory_name or "Authorized Signatory",
    )

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 9)

    pdf.drawCentredString(
        signature_x + 57,
        signature_y - 22,
        certificate.signatory_position or "Institution",
    )

    # --------------------------------------------------
    # 11. CERTIFICATE NUMBER
    # --------------------------------------------------

    pdf.setFillColor(colors.HexColor("#163B65"))
    pdf.setFont("Helvetica-Bold", 9)

    pdf.drawString(
        55,
        72,
        f"Certificate No: {certificate.certificate_number}",
    )

    # --------------------------------------------------
    # 12. PUBLIC VERIFICATION REFERENCE
    # --------------------------------------------------

    pdf.setFillColor(colors.HexColor("#444444"))
    pdf.setFont("Helvetica", 8)

    pdf.drawString(
        55,
        55,
        "Verify this certificate using the reference below:",
    )

    verification_lines = simpleSplit(
        verification_url,
        "Helvetica",
        7,
        390,
    )

    verification_y = 43

    for line in verification_lines[:2]:
        pdf.drawString(
            55,
            verification_y,
            line,
        )

        verification_y -= 9

    # --------------------------------------------------
    # 13. FOOTER
    # --------------------------------------------------

    if certificate.footer_text:
        pdf.setFillColor(colors.HexColor("#555555"))
        pdf.setFont("Helvetica-Oblique", 8)

        pdf.drawCentredString(
            page_width / 2,
            32,
            certificate.footer_text[:180],
        )

    # --------------------------------------------------
    # 14. FINISH PDF
    # --------------------------------------------------

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()