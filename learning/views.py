import json

from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from courses.models import Lesson
from subscriptions.models import Subscription

from .models import LessonQuestion, LessonAnswer


User = get_user_model()


# =====================================================
# USER ROLE CHECKS
# =====================================================

def is_administrator(user):

    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.role == User.Role.ADMINISTRATOR
        )
    )


def is_instructor(user, lesson):

    return (
        user.is_authenticated
        and user.role == User.Role.INSTRUCTOR
        and lesson.module.course.instructor_id == user.pk
    )


def can_access_lesson(user, lesson):

    if not user.is_authenticated:
        return False

    if is_administrator(user):
        return True

    if is_instructor(user, lesson):
        return True

    # Students can access free preview lessons.
    if lesson.is_free_preview:
        return True

    now = timezone.now()

    return Subscription.objects.filter(
        user=user,
        plan__course=lesson.module.course,
        status=Subscription.Status.ACTIVE,
        starts_at__lte=now,
        ends_at__gt=now,
    ).exists()


def get_lesson(lesson_id):

    return get_object_or_404(
        Lesson.objects.select_related(
            "module",
            "module__course",
            "module__course__instructor",
        ),
        pk=lesson_id,
        is_published=True,
        module__is_published=True,
        module__course__is_published=True,
    )


# =====================================================
# JSON HELPERS
# =====================================================

def get_json_data(request):

    try:
        return json.loads(request.body)

    except (json.JSONDecodeError, UnicodeDecodeError):

        return None


def user_display_name(user):

    return (
        user.get_full_name().strip()
        or user.username
    )


def question_data(question, current_user):

    answers = question.answers.filter(
        is_hidden=False
    ).select_related("user")

    return {
        "id": question.pk,

        "question": question.question,

        "student": user_display_name(
            question.student
        ),

        "student_id": question.student_id,

        "created_at": question.created_at.isoformat(),

        "updated_at": question.updated_at.isoformat(),

        "is_resolved": question.is_resolved,

        "can_edit": (
            question.student_id == current_user.pk
        ),

        "can_delete": (
            question.student_id == current_user.pk
            or is_administrator(current_user)
        ),

        "answers": [

            {
                "id": answer.pk,

                "answer": answer.answer,

                "user": user_display_name(
                    answer.user
                ),

                "user_id": answer.user_id,

                "is_instructor_answer": (
                    answer.is_instructor_answer
                ),

                "created_at": (
                    answer.created_at.isoformat()
                ),

                "updated_at": (
                    answer.updated_at.isoformat()
                ),

                "can_edit": (
                    answer.user_id == current_user.pk
                ),

                "can_delete": (
                    answer.user_id == current_user.pk
                    or is_administrator(current_user)
                ),

            }

            for answer in answers

        ],

    }


# =====================================================
# LIST QUESTIONS AND SUBMIT QUESTIONS
# =====================================================

@require_http_methods(["GET", "POST"])
def lesson_questions(request, lesson_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {
                "success": False,
                "message": "Please log in to access lesson discussions."
            },
            status=401
        )

    lesson = get_lesson(lesson_id)

    if not can_access_lesson(request.user, lesson):

        return JsonResponse(
            {
                "success": False,
                "message": "You do not have access to this lesson."
            },
            status=403
        )

    # -----------------------------------------------
    # GET QUESTIONS
    # -----------------------------------------------

    if request.method == "GET":

        questions = LessonQuestion.objects.filter(
            lesson=lesson,
            is_hidden=False,
        ).select_related(
            "student"
        ).prefetch_related(
            Prefetch(
                "answers",
                queryset=LessonAnswer.objects.filter(
                    is_hidden=False
                ).select_related("user")
            )
        )

        return JsonResponse({

            "success": True,

            "lesson": lesson.title,

            "questions": [

                question_data(
                    question,
                    request.user
                )

                for question in questions

            ]

        })

    # -----------------------------------------------
    # POST QUESTION
    # -----------------------------------------------

    if request.user.role != User.Role.STUDENT:

        return JsonResponse(
            {
                "success": False,
                "message": "Only students can submit lesson questions."
            },
            status=403
        )

    data = get_json_data(request)

    if data is None:

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request data."
            },
            status=400
        )

    question_text = data.get("question", "").strip()

    if not question_text:

        return JsonResponse(
            {
                "success": False,
                "message": "Please enter your question."
            },
            status=400
        )

    if len(question_text) > 10000:

        return JsonResponse(
            {
                "success": False,
                "message": "Your question is too long."
            },
            status=400
        )

    question = LessonQuestion.objects.create(

        lesson=lesson,

        student=request.user,

        question=question_text,

    )

    return JsonResponse({

        "success": True,

        "message": "Your question has been submitted.",

        "question": question_data(
            question,
            request.user
        )

    }, status=201)


# =====================================================
# EDIT QUESTION
# =====================================================

@require_http_methods(["POST"])
def edit_question(request, question_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    question = get_object_or_404(
        LessonQuestion.objects.select_related(
            "lesson__module__course"
        ),
        pk=question_id
    )

    if question.student_id != request.user.pk:

        return JsonResponse(
            {
                "success": False,
                "message": "You can only edit your own questions."
            },
            status=403
        )

    if not can_access_lesson(
        request.user,
        question.lesson
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "You no longer have access to this lesson."
            },
            status=403
        )

    if question.is_hidden:

        return JsonResponse(
            {
                "success": False,
                "message": "This question is unavailable for editing."
            },
            status=403
        )

    data = get_json_data(request)

    if data is None:

        return JsonResponse(
            {"success": False, "message": "Invalid request data."},
            status=400
        )

    question_text = data.get("question", "").strip()

    if not question_text:

        return JsonResponse(
            {
                "success": False,
                "message": "Question cannot be empty."
            },
            status=400
        )

    if len(question_text) > 10000:

        return JsonResponse(
            {
                "success": False,
                "message": "Your question is too long."
            },
            status=400
        )

    question.question = question_text

    question.save(update_fields=[
        "question",
        "updated_at"
    ])

    return JsonResponse({

        "success": True,

        "message": "Question updated successfully."

    })


# =====================================================
# DELETE QUESTION
# =====================================================

@require_http_methods(["POST"])
def delete_question(request, question_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    question = get_object_or_404(
        LessonQuestion,
        pk=question_id
    )

    if not (
        question.student_id == request.user.pk
        or is_administrator(request.user)
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "You cannot delete this question."
            },
            status=403
        )

    question.delete()

    return JsonResponse({

        "success": True,

        "message": "Question deleted successfully."

    })


# =====================================================
# SUBMIT ANSWER OR REPLY
# =====================================================

@require_http_methods(["POST"])
def submit_answer(request, question_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    question = get_object_or_404(
        LessonQuestion.objects.select_related(
            "lesson__module__course"
        ),
        pk=question_id,
        is_hidden=False,
        lesson__is_published=True,
        lesson__module__is_published=True,
        lesson__module__course__is_published=True,
    )

    if not can_access_lesson(
        request.user,
        question.lesson
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "You do not have access to this lesson."
            },
            status=403
        )

    data = get_json_data(request)

    if data is None:

        return JsonResponse(
            {"success": False, "message": "Invalid request data."},
            status=400
        )

    answer_text = data.get("answer", "").strip()

    if not answer_text:

        return JsonResponse(
            {
                "success": False,
                "message": "Please enter your answer."
            },
            status=400
        )

    if len(answer_text) > 10000:

        return JsonResponse(
            {
                "success": False,
                "message": "Your answer is too long."
            },
            status=400
        )

    official_answer = is_instructor(
        request.user,
        question.lesson
    )

    answer = LessonAnswer.objects.create(

        question=question,

        user=request.user,

        answer=answer_text,

        is_instructor_answer=official_answer,

    )

    return JsonResponse({

        "success": True,

        "message": (
            "Instructor answer submitted successfully."
            if official_answer
            else "Your reply has been submitted."
        ),

        "answer": {

            "id": answer.pk,

            "answer": answer.answer,

            "user": user_display_name(
                answer.user
            ),

            "is_instructor_answer": (
                answer.is_instructor_answer
            ),

        }

    }, status=201)


# =====================================================
# EDIT ANSWER
# =====================================================

@require_http_methods(["POST"])
def edit_answer(request, answer_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    answer = get_object_or_404(
        LessonAnswer.objects.select_related(
            "question__lesson__module__course"
        ),
        pk=answer_id
    )

    if answer.user_id != request.user.pk:

        return JsonResponse(
            {
                "success": False,
                "message": "You can only edit your own replies."
            },
            status=403
        )

    if answer.is_hidden:

        return JsonResponse(
            {
                "success": False,
                "message": "This answer is unavailable for editing."
            },
            status=403
        )

    if answer.question.is_hidden:

        return JsonResponse(
            {
                "success": False,
                "message": "This discussion is unavailable."
            },
            status=403
        )

    if not can_access_lesson(
        request.user,
        answer.question.lesson
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "You do not have access to this lesson."
            },
            status=403
        )

    data = get_json_data(request)

    if data is None:

        return JsonResponse(
            {"success": False, "message": "Invalid request data."},
            status=400
        )

    answer_text = data.get("answer", "").strip()

    if not answer_text:

        return JsonResponse(
            {
                "success": False,
                "message": "Answer cannot be empty."
            },
            status=400
        )

    if len(answer_text) > 10000:

        return JsonResponse(
            {
                "success": False,
                "message": "Your answer is too long."
            },
            status=400
        )

    answer.answer = answer_text

    answer.save(update_fields=[
        "answer",
        "updated_at"
    ])

    return JsonResponse({

        "success": True,

        "message": "Reply updated successfully."

    })


# =====================================================
# DELETE ANSWER
# =====================================================

@require_http_methods(["POST"])
def delete_answer(request, answer_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    answer = get_object_or_404(
        LessonAnswer,
        pk=answer_id
    )

    if not (
        answer.user_id == request.user.pk
        or is_administrator(request.user)
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "You cannot delete this reply."
            },
            status=403
        )

    answer.delete()

    return JsonResponse({

        "success": True,

        "message": "Reply deleted successfully."

    })


# =====================================================
# MARK QUESTION AS RESOLVED
# =====================================================

@require_http_methods(["POST"])
def resolve_question(request, question_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    question = get_object_or_404(
        LessonQuestion.objects.select_related(
            "lesson__module__course"
        ),
        pk=question_id
    )

    authorized = (
        is_administrator(request.user)
        or is_instructor(
            request.user,
            question.lesson
        )
    )

    if not authorized:

        return JsonResponse(
            {
                "success": False,
                "message": "Only the course instructor or administrator can resolve questions."
            },
            status=403
        )

    if question.is_hidden:

        return JsonResponse(
            {
                "success": False,
                "message": "Hidden questions cannot be resolved."
            },
            status=403
        )

    question.is_resolved = True

    question.save(update_fields=[
        "is_resolved",
        "updated_at"
    ])

    return JsonResponse({

        "success": True,

        "message": "Question marked as resolved."

    })


# =====================================================
# ADMINISTRATOR MODERATION
# =====================================================

@require_http_methods(["POST"])
def moderate_question(request, question_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    if not is_administrator(request.user):

        return JsonResponse(
            {
                "success": False,
                "message": "Administrator permission required."
            },
            status=403
        )

    question = get_object_or_404(
        LessonQuestion,
        pk=question_id
    )

    data = get_json_data(request)

    if data is None:

        return JsonResponse(
            {"success": False, "message": "Invalid request data."},
            status=400
        )

    question.is_hidden = bool(
        data.get("is_hidden")
    )

    question.save(update_fields=[
        "is_hidden",
        "updated_at"
    ])

    return JsonResponse({

        "success": True,

        "message": (
            "Question hidden successfully."
            if question.is_hidden
            else "Question restored successfully."
        )

    })


@require_http_methods(["POST"])
def moderate_answer(request, answer_id):

    if not request.user.is_authenticated:

        return JsonResponse(
            {"success": False, "message": "Please log in."},
            status=401
        )

    if not is_administrator(request.user):

        return JsonResponse(
            {
                "success": False,
                "message": "Administrator permission required."
            },
            status=403
        )

    answer = get_object_or_404(
        LessonAnswer,
        pk=answer_id
    )

    data = get_json_data(request)

    if data is None:

        return JsonResponse(
            {"success": False, "message": "Invalid request data."},
            status=400
        )

    answer.is_hidden = bool(
        data.get("is_hidden")
    )

    answer.save(update_fields=[
        "is_hidden",
        "updated_at"
    ])

    return JsonResponse({

        "success": True,

        "message": (
            "Answer hidden successfully."
            if answer.is_hidden
            else "Answer restored successfully."
        )

    })