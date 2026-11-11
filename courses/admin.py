from django.contrib import admin
from .models import (
    Category,
    Course,
    Module,
    Lesson,
    Advertisement,
    LessonProgress,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    search_fields = ("name",)

    list_filter = ("is_active",)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "instructor",
        "level",
        "is_published",
    )

    list_filter = (
        "level",
        "is_published",
        "category",
    )

    search_fields = (
        "title",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    inlines = [ModuleInline]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "order",
        "is_published",
    )

    list_filter = ("is_published",)

    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "module",
        "order",
        "duration_minutes",
        "is_free_preview",
        "is_published",
    )

    list_filter = (
        "is_published",
        "is_free_preview",
    )

    search_fields = ("title",)


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "placement",
        "is_active",
        "display_order",
        "start_at",
        "end_at",
    )

    list_filter = (
        "placement",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    list_editable = (
        "is_active",
        "display_order",
    )

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Advertisement Information", {
            "fields": (
                "title",
                "description",
                "image",
                "target_url",
            )
        }),

        ("Display Settings", {
            "fields": (
                "placement",
                "is_active",
                "display_order",
            )
        }),

        ("Advertisement Schedule", {
            "fields": (
                "start_at",
                "end_at",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
            )
        }),
    )




@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "lesson",
        "last_position",
        "video_duration",
        "is_completed",
        "last_watched",
    )

    list_filter = (
        "is_completed",
        "last_watched",
    )

    search_fields = (
        "user__email",
        "lesson__title",
    )

    readonly_fields = (
        "last_watched",
        "completed_at",
    )    