from django.contrib import admin

from .models import CertificateSettings, Certificate


@admin.register(CertificateSettings)
class CertificateSettingsAdmin(admin.ModelAdmin):

    fieldsets = (

        (
            "Institution Information",
            {
                "fields": (
                    "institution_name",
                    "institution_logo",
                )
            },
        ),

        (
            "Certificate Design",
            {
                "fields": (
                    "certificate_title",
                    "certificate_background",
                    "description",
                )
            },
        ),

        (
            "Authorised Signatory",
            {
                "fields": (
                    "signatory_name",
                    "signatory_position",
                    "signature_image",
                )
            },
        ),

        (
            "Certificate Identification",
            {
                "fields": (
                    "certificate_prefix",
                    "auto_issue",
                )
            },
        ),

        (
            "Footer Information",
            {
                "fields": (
                    "footer_text",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "updated_at",
    )

    def has_add_permission(self, request):
        return not CertificateSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):

    list_display = (
        "certificate_number",
        "student_name",
        "course_title",
        "issued_at",
        "status",
    )

    list_filter = (
        "status",
        "issued_at",
    )

    search_fields = (
        "certificate_number",
        "student_name",
        "user__email",
        "course_title",
    )

    readonly_fields = (
        "user",
        "course",
        "certificate_number",
        "issued_at",
        "student_name",
        "course_title",
        "institution_name",
        "certificate_title",
        "description",
        "signatory_name",
        "signatory_position",
        "footer_text",
        "institution_logo_snapshot",
        "signature_snapshot",
        "background_snapshot",
    )

    fieldsets = (

        (
            "Certificate Information",
            {
                "fields": (
                    "certificate_number",
                    "user",
                    "course",
                    "issued_at",
                    "status",
                )
            },
        ),

        (
            "Student and Course Details",
            {
                "fields": (
                    "student_name",
                    "course_title",
                )
            },
        ),

        (
            "Certificate Design Snapshot",
            {
                "fields": (
                    "institution_name",
                    "certificate_title",
                    "description",
                    "signatory_name",
                    "signatory_position",
                    "footer_text",
                    "institution_logo_snapshot",
                    "signature_snapshot",
                    "background_snapshot",
                )
            },
        ),

        (
            "Revocation Information",
            {
                "fields": (
                    "revoked_at",
                    "revocation_reason",
                )
            },
        ),
    )