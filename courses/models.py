from django.db import models
from django.conf import settings
from django.utils.text import slugify
from .storage import PrivateVideoStorage

class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="courses",
    )
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="courses_taught",
    )
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
    )
    thumbnail = models.ImageField(
        upload_to="courses/thumbnails/",
        blank=True,
        null=True,
    )

    # Optional course introduction video URL.
    # Lesson videos themselves must be uploaded as files.
    preview_video_url = models.URLField(blank=True)

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "course"
            candidate_slug = base_slug
            counter = 1

            while Course.objects.filter(
                slug=candidate_slug
            ).exclude(pk=self.pk).exists():
                counter += 1
                candidate_slug = f"{base_slug}-{counter}"

            self.slug = candidate_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"],
                name="unique_module_order_per_course",
            )
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Instructor-uploaded lesson video.
    video_file = models.FileField(
        storage=PrivateVideoStorage(),
        upload_to="courses/videos/",
        blank=True,
        null=True,
    )

    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=1)
    is_free_preview = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "order"],
                name="unique_lesson_order_per_module",
            )
        ]

    def __str__(self):
        return f"{self.module.title} - {self.title}"



class Advertisement(models.Model):

    class Placement(models.TextChoices):
        HOMEPAGE = "homepage", "Homepage"
        COURSE = "course", "Course Pages"

    title = models.CharField(max_length=200)

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="advertisements/",
    )

    target_url = models.URLField(
        blank=True,
        help_text="Where visitors should go when they click the advertisement."
    )

    category = models.ForeignKey(
    Category,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="advertisements",
    help_text="Select the learning category this advertisement should open."
)


    placement = models.CharField(
        max_length=20,
        choices=Placement.choices,
        default=Placement.HOMEPAGE,
    )

    is_active = models.BooleanField(
        default=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    start_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional date and time when the advertisement should start."
    )

    end_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional date and time when the advertisement should stop."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="student_progress",
    )

    # Last position where the student stopped watching, in seconds.
    last_position = models.FloatField(default=0)

    # Actual video duration, in seconds.
    video_duration = models.FloatField(default=0)

    # Whether the student has completed this lesson.
    is_completed = models.BooleanField(default=False)

    # Date and time the lesson was completed.
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    # Automatically updated whenever progress is saved.
    last_watched = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_watched"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_student_lesson_progress",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.lesson.title}"




class LessonNote(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_notes",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="student_notes",
    )

    content = models.TextField(
        blank=True,
        help_text="Personal notes written by the student."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_student_note_per_lesson",
            )
        ]

    def __str__(self):
        return f"{self.user} - Notes for {self.lesson.title}"


class LessonBookmark(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_bookmarks",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="student_bookmarks",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_student_lesson_bookmark",
            )
        ]

    def __str__(self):
        return f"{self.user} bookmarked {self.lesson.title}"


class CourseReview(models.Model):

    RATING_CHOICES = [
        (1, "1 Star - Poor"),
        (2, "2 Stars - Fair"),
        (3, "3 Stars - Good"),
        (4, "4 Stars - Very Good"),
        (5, "5 Stars - Excellent"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
    )

    review = models.TextField(
        blank=True,
        help_text="Share your experience with this course."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_student_course_review",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    rating__gte=1,
                    rating__lte=5,
                ),
                name="valid_course_review_rating",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.course.title} ({self.rating}/5)"
