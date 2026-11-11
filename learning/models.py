from django.db import models
from django.conf import settings


class LessonQuestion(models.Model):

    lesson = models.ForeignKey(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="questions"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_questions"
    )

    question = models.TextField(
        help_text="Enter your question about this lesson."
    )

    is_resolved = models.BooleanField(
        default=False
    )

    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden questions are not visible to students."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["lesson", "created_at"],
                name="lesson_question_date_idx"
            ),
            models.Index(
                fields=["student", "created_at"],
                name="student_question_date_idx"
            ),
        ]

    def __str__(self):
        return f"Question by {self.student} - {self.lesson.title}"


class LessonAnswer(models.Model):

    question = models.ForeignKey(
        LessonQuestion,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_answers"
    )

    answer = models.TextField(
        help_text="Enter your response."
    )

    is_instructor_answer = models.BooleanField(
        default=False
    )

    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden answers are not visible to students."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["question", "created_at"],
                name="lesson_answer_date_idx"
            ),
        ]

    def __str__(self):
        return f"Answer by {self.user} to Question #{self.question.pk}"
