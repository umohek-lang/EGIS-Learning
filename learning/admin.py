from django.contrib import admin
from .models import LessonQuestion, LessonAnswer


class LessonAnswerInline(admin.TabularInline):
    model = LessonAnswer
    extra = 0

    fields = (
        "user",
        "answer",
        "is_instructor_answer",
        "is_hidden",
        "created_at",
    )

    readonly_fields = ("created_at",)

    show_change_link = True


@admin.register(LessonQuestion)
class LessonQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "student",
        "get_lesson",
        "is_resolved",
        "is_hidden",
        "created_at",
    )

    list_filter = (
        "is_resolved",
        "is_hidden",
        "created_at",
    )

    search_fields = (
        "question",
        "student__username",
        "student__email",
        "lesson__title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [LessonAnswerInline]

    list_per_page = 25

    @admin.display(description="Lesson")
    def get_lesson(self, obj):
        return obj.lesson.title

    actions = [
        "mark_resolved",
        "mark_unresolved",
        "hide_questions",
        "show_questions",
    ]

    @admin.action(description="Mark selected questions as resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)

    @admin.action(description="Reopen selected questions")
    def mark_unresolved(self, request, queryset):
        queryset.update(is_resolved=False)

    @admin.action(description="Hide selected questions")
    def hide_questions(self, request, queryset):
        queryset.update(is_hidden=True)

    @admin.action(description="Show selected questions")
    def show_questions(self, request, queryset):
        queryset.update(is_hidden=False)


@admin.register(LessonAnswer)
class LessonAnswerAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "question",
        "user",
        "is_instructor_answer",
        "is_hidden",
        "created_at",
    )

    list_filter = (
        "is_instructor_answer",
        "is_hidden",
        "created_at",
    )

    search_fields = (
        "answer",
        "user__username",
        "user__email",
        "question__question",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 25

    actions = [
        "hide_answers",
        "show_answers",
    ]

    @admin.action(description="Hide selected answers")
    def hide_answers(self, request, queryset):
        queryset.update(is_hidden=True)

    @admin.action(description="Show selected answers")
    def show_answers(self, request, queryset):
        queryset.update(is_hidden=False)