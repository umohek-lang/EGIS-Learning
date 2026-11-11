import json
import math
import mimetypes

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods

from .forms import LessonForm

from .models import (
    Category,
    Course,
    Module,
    Lesson,
    Advertisement,
    LessonProgress,
    LessonNote,
    LessonBookmark,
)

from subscriptions.models import Subscription
from certificates.services import issue_certificate_if_eligible

def has_active_subscription(user, course):
    """
    Check whether the user has an active subscription
    for this particular course.
    """

    if not user.is_authenticated:
        return False

    now = timezone.now()

    return Subscription.objects.filter(
        user=user,
        plan__course=course,
        status=Subscription.Status.ACTIVE,
        starts_at__lte=now,
        ends_at__gt=now,
    ).exists()


def home(request):

    now = timezone.now()

    categories = Category.objects.filter(
        is_active=True
    )

    courses = Course.objects.filter(
        is_published=True,
        category__is_active=True,
    ).select_related(
        "category",
        "instructor",
    )

    advertisements = Advertisement.objects.filter(
        is_active=True,
        placement=Advertisement.Placement.HOMEPAGE,
    ).filter(
        models.Q(start_at__isnull=True) |
        models.Q(start_at__lte=now)
    ).filter(
        models.Q(end_at__isnull=True) |
        models.Q(end_at__gt=now)
    )

    return render(
        request,
        "courses/home.html",
        {
            "categories": categories,
            "courses": courses,
            "advertisements": advertisements,
        },
    )


def training_list(request):
    """
    Display all published courses and active categories.
    """

    categories = Category.objects.filter(
        is_active=True
    )

    courses = Course.objects.filter(
        is_published=True,
        category__is_active=True,
    ).select_related(
        "category",
        "instructor",
    )

    return render(
        request,
        "courses/training_list.html",
        {
            "categories": categories,
            "courses": courses,
        },
    )


def category_courses(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True,
    )

    courses = Course.objects.filter(
        category=category,
        is_published=True,
    ).select_related(
        "category",
        "instructor",
    )

    return render(
        request,
        "courses/category_courses.html",
        {
            "category": category,
            "courses": courses,
        },
    )


def course_detail(request, slug):

    course = get_object_or_404(
        Course.objects.select_related(
            "category",
            "instructor",
        ),
        slug=slug,
        is_published=True,
        category__is_active=True,
    )

    # Check subscription for this particular course.
    subscription_active = has_active_subscription(
        request.user,
        course,
    )

    modules = list(
        course.modules.filter(
            is_published=True,
        ).prefetch_related("lessons")
    )

    accessible_lessons = []

    for module in modules:

        module.visible_lessons = []

        for lesson in module.lessons.all():

            if not lesson.is_published:
                continue

            lesson.can_watch = (
                lesson.is_free_preview or subscription_active
            )

            lesson.has_video = bool(lesson.video_file)

            # Default progress values.
            lesson.is_completed = False
            lesson.saved_position = 0

            module.visible_lessons.append(lesson)

            if lesson.can_watch and lesson.has_video:
                accessible_lessons.append(lesson)

    # Default course progress values.
    progress_percentage = 0
    completed_lessons = 0
    # total_lessons = len([
    #     lesson
    #     for module in modules
    #     for lesson in module.visible_lessons
    #     if lesson.has_video
    # ])
    total_lessons = 0

    total_lessons = len(accessible_lessons)
    resume_lesson_id = None
    resume_position = 0

    if request.user.is_authenticated:

        # Retrieve only this student's progress for this course.
        progress_records = list(
            LessonProgress.objects.filter(
                user=request.user,
                lesson__module__course=course,
                lesson__is_published=True,
                lesson__module__is_published=True,
            ).select_related(
                "lesson"
            ).order_by(
                "-last_watched"
            )
        )

        progress_by_lesson = {
            record.lesson_id: record
            for record in progress_records
        }

        # Attach progress information to each visible lesson.
        for module in modules:

            for lesson in module.visible_lessons:

                record = progress_by_lesson.get(lesson.pk)

                if record:

                    lesson.is_completed = record.is_completed

                    lesson.saved_position = (
                        record.last_position
                    )

        # Calculate course completion.
        completed_lessons = sum(
            1
            for lesson in accessible_lessons
            if progress_by_lesson.get(lesson.pk)
            and progress_by_lesson[lesson.pk].is_completed
        )

        if total_lessons > 0:

            progress_percentage = round(
                (completed_lessons / total_lessons) * 100
            )

        # Determine which lesson the student should resume.
        if accessible_lessons:

            accessible_ids = {
                lesson.pk: index
                for index, lesson in enumerate(accessible_lessons)
            }

            # First preference: most recently watched incomplete lesson.
            latest_incomplete = next(
                (
                    record
                    for record in progress_records
                    if (
                        not record.is_completed
                        and record.lesson_id in accessible_ids
                    )
                ),
                None,
            )

            if latest_incomplete:

                resume_lesson_id = latest_incomplete.lesson_id
                resume_position = latest_incomplete.last_position

            else:

                # If the last lesson was completed, continue to the next
                # accessible lesson.
                latest_record = (
                    progress_records[0]
                    if progress_records
                    else None
                )

                if (
                    latest_record
                    and latest_record.is_completed
                    and latest_record.lesson_id in accessible_ids
                ):

                    current_index = accessible_ids[
                        latest_record.lesson_id
                    ]

                    next_index = current_index + 1

                    if next_index < len(accessible_lessons):

                        resume_lesson_id = (
                            accessible_lessons[next_index].pk
                        )

                # If no suitable previous lesson exists, select the
                # first incomplete accessible lesson.
                if resume_lesson_id is None:

                    first_incomplete = next(
                        (
                            lesson
                            for lesson in accessible_lessons
                            if (
                                not progress_by_lesson.get(lesson.pk)
                                or not progress_by_lesson[
                                    lesson.pk
                                ].is_completed
                            )
                        ),
                        None,
                    )

                    if first_incomplete:

                        resume_lesson_id = first_incomplete.pk

                    else:

                        # All accessible lessons have been completed.
                        # Select the first lesson for replay.
                        resume_lesson_id = accessible_lessons[0].pk

    else:

        # Visitors can watch free previews but progress is not
        # saved to an account.
        if accessible_lessons:
            resume_lesson_id = accessible_lessons[0].pk
        
        
         # Student bookmark information.
    bookmarked_lesson_ids = set()

    if request.user.is_authenticated and accessible_lessons:

        bookmarked_lesson_ids = set(
            LessonBookmark.objects.filter(
                user=request.user,
                lesson__in=accessible_lessons,
            ).values_list("lesson_id", flat=True)
        )

    # Attach bookmark status to each visible lesson.
    for module in modules:
        for lesson in module.visible_lessons:
            lesson.is_bookmarked = lesson.pk in bookmarked_lesson_ids   
    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "modules": modules,
            "has_active_subscription": subscription_active,

            # Progress information.
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "progress_percentage": progress_percentage,

            # Resume information.
            "resume_lesson_id": resume_lesson_id,
            "resume_position": resume_position,
        },
    )


def lesson_video_file(request, lesson_id):
    """
    Serve an uploaded lesson video only if the lesson is a free
    preview or the user has an active subscription for its course.
    """

    lesson = get_object_or_404(
        Lesson.objects.select_related(
            "module__course",
            "module__course__category",
        ),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
        module__course__is_published=True,
        module__course__category__is_active=True,
    )

    if not lesson.video_file:
        raise Http404("Uploaded video not found.")

    if not lesson.is_free_preview:

        course = lesson.module.course

        subscription_active = has_active_subscription(
            request.user,
            course,
        )

        if not subscription_active:
            raise Http404("An active subscription is required.")

    try:
        video = lesson.video_file.open("rb")

    except (OSError, ValueError):
        raise Http404("Video file is unavailable.")

    content_type, _ = mimetypes.guess_type(
        lesson.video_file.name
    )

    if not content_type or not content_type.startswith("video/"):
        video.close()
        raise Http404("Unsupported video file type.")

    response = FileResponse(
        video,
        content_type=content_type,
    )

    response["Content-Disposition"] = "inline"
    response["X-Content-Type-Options"] = "nosniff"

    return response


@login_required
@require_POST
def save_lesson_progress(request, lesson_id):
    """
    Save the logged-in student's playback position.

    A student can only save progress for lessons they are
    currently allowed to watch.

    Automatically issue a certificate when the student
    completes all required lessons in the course.
    """

    lesson = get_object_or_404(
        Lesson.objects.select_related(
            "module__course",
            "module__course__category",
        ),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
        module__course__is_published=True,
        module__course__category__is_active=True,
    )

    # Enforce the same lesson access rules as video streaming.
    if not lesson.is_free_preview:

        subscription_active = has_active_subscription(
            request.user,
            lesson.module.course,
        )

        if not subscription_active:

            return JsonResponse(
                {
                    "success": False,
                    "message": "An active course subscription is required.",
                },
                status=403,
            )

    try:

        data = json.loads(request.body)

        position = float(data.get("position", 0))
        duration = float(data.get("duration", 0))
        ended = data.get("ended", False)

        if (
            not math.isfinite(position)
            or not math.isfinite(duration)
            or position < 0
            or duration < 0
            or duration > 86400
        ):
            raise ValueError

        if not isinstance(ended, bool):
            raise ValueError

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid progress information.",
            },
            status=400,
        )

    if duration > 0:
        position = min(position, duration)

    # Mark completed when the video ends or the student reaches 90%.
    completed = (
        ended
        or (
            duration > 0
            and position >= duration * 0.90
        )
    )

    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={
            "last_position": position,
            "video_duration": duration,
            "is_completed": completed,
            "completed_at": timezone.now() if completed else None,
        },
    )

    if not created:

        progress.last_position = position

        if duration > 0:
            progress.video_duration = duration

        # Never reverse a completed lesson to incomplete.
        if completed and not progress.is_completed:

            progress.is_completed = True
            progress.completed_at = timezone.now()

        progress.save()

    # ==========================================
    # AUTOMATIC CERTIFICATE ISSUANCE
    # ==========================================

    certificate = None

    if progress.is_completed:

        certificate = issue_certificate_if_eligible(
            request.user,
            lesson.module.course,
        )

    certificate_issued = (
        certificate is not None
        and certificate.status == "issued"
    )

    return JsonResponse(
        {
            "success": True,
            "lesson_id": lesson.pk,
            "position": progress.last_position,
            "is_completed": progress.is_completed,
            "certificate_issued": certificate_issued,
            "certificate_number": (
                certificate.certificate_number
                if certificate_issued
                else None
            ),
            "message": "Progress saved successfully.",
        }
    )

@login_required
def create_lesson(request, module_id):

    module = get_object_or_404(
        Module.objects.select_related(
            "course",
            "course__instructor",
        ),
        pk=module_id,
    )

    # Only the instructor who owns this course can add lessons.
    if module.course.instructor_id != request.user.pk:
        raise Http404("You are not allowed to manage this course.")

    if request.method == "POST":

        form = LessonForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            lesson = form.save(commit=False)
            lesson.module = module

            # Prevent two lessons from having the same order.
            if Lesson.objects.filter(
                module=module,
                order=lesson.order,
            ).exists():

                form.add_error(
                    "order",
                    "This lesson order is already in use in this module.",
                )

            else:

                lesson.save()

                messages.success(
                    request,
                    "Lesson created successfully.",
                )

                return redirect(
                    "course_detail",
                    slug=module.course.slug,
                )

    else:
        form = LessonForm()

    return render(
        request,
        "courses/instructor/lesson_form.html",
        {
            "form": form,
            "module": module,
            "course": module.course,
        },
    )

def advertisement_detail(request, pk):

    from django.utils import timezone
    from django.db import models

    now = timezone.now()

    advertisement = get_object_or_404(
        Advertisement.objects.filter(
            is_active=True
        ).filter(
            models.Q(start_at__isnull=True) |
            models.Q(start_at__lte=now)
        ).filter(
            models.Q(end_at__isnull=True) |
            models.Q(end_at__gt=now)
        ),
        pk=pk
    )

    return render(
        request,
        "courses/advertisement_detail.html",
        {
            "advertisement": advertisement
        }
    )




@login_required
@require_http_methods(["GET", "POST"])
def lesson_notes(request, lesson_id):
    """
    Retrieve or save personal notes for a particular lesson.

    Each student can only access their own notes.

    Students must be allowed to watch the lesson
    before accessing its notes.
    """

    lesson = get_object_or_404(
        Lesson.objects.select_related(
            "module__course",
            "module__course__category",
        ),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
        module__course__is_published=True,
        module__course__category__is_active=True,
    )

    # Check whether the student can access this lesson.
    if not lesson.is_free_preview:

        subscription_active = has_active_subscription(
            request.user,
            lesson.module.course,
        )

        if not subscription_active:

            return JsonResponse(
                {
                    "success": False,
                    "message": "An active course subscription is required."
                },
                status=403,
            )

    # Retrieve this student's notes for this lesson.
    note = LessonNote.objects.filter(
        user=request.user,
        lesson=lesson,
    ).first()

    # ==========================================
    # GET: LOAD EXISTING NOTES
    # ==========================================

    if request.method == "GET":

        return JsonResponse(
            {
                "success": True,
                "content": note.content if note else "",
                "updated_at": (
                    note.updated_at.strftime("%d %B %Y, %I:%M %p")
                    if note else None
                ),
            }
        )

    # ==========================================
    # POST: SAVE OR UPDATE NOTES
    # ==========================================

    try:

        data = json.loads(request.body)

        content = data.get("content", "")

        if not isinstance(content, str):
            raise ValueError

        content = content.strip()

        if len(content) > 20000:

            return JsonResponse(
                {
                    "success": False,
                    "message": "Your notes cannot exceed 20,000 characters."
                },
                status=400,
            )

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid notes information."
            },
            status=400,
        )

    note, created = LessonNote.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={
            "content": content,
        }
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Your notes have been saved successfully.",
            "content": note.content,
            "updated_at": note.updated_at.strftime(
                "%d %B %Y, %I:%M %p"
            ),
        }
    )



@login_required
@require_POST
def lesson_bookmark(request, lesson_id):
    """
    Add or remove a student's bookmark for a lesson.

    Each student can only manage their own bookmarks.
    """

    # Retrieve only published lessons and courses.
    lesson = get_object_or_404(
        Lesson.objects.select_related(
            "module__course",
            "module__course__category",
        ),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
        module__course__is_published=True,
        module__course__category__is_active=True,
    )

    # Check lesson access.
    if not lesson.is_free_preview:

        subscription_active = has_active_subscription(
            request.user,
            lesson.module.course,
        )

        if not subscription_active:

            return JsonResponse(
                {
                    "success": False,
                    "message": "An active course subscription is required."
                },
                status=403,
            )

    # Read the requested action.
    try:

        data = json.loads(request.body)

        action = data.get("action")

        if action not in ["add", "remove"]:
            raise ValueError

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid bookmark request."
            },
            status=400,
        )

    # ADD BOOKMARK
    if action == "add":

        bookmark, created = LessonBookmark.objects.get_or_create(
            user=request.user,
            lesson=lesson,
        )

        return JsonResponse(
            {
                "success": True,
                "bookmarked": True,
                "message": (
                    "Lesson bookmarked successfully."
                    if created
                    else "This lesson is already bookmarked."
                ),
            }
        )

    # REMOVE BOOKMARK
    if action == "remove":

        deleted_count, _ = LessonBookmark.objects.filter(
            user=request.user,
            lesson=lesson,
        ).delete()

        return JsonResponse(
            {
                "success": True,
                "bookmarked": False,
                "message": (
                    "Bookmark removed successfully."
                    if deleted_count
                    else "This lesson was not bookmarked."
                ),
            }
        )