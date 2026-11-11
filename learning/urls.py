from django.urls import path

from . import views


urlpatterns = [

    # List questions and submit a new question.
    path(
        "lessons/<int:lesson_id>/questions/",
        views.lesson_questions,
        name="lesson_questions"
    ),

    # Edit and delete questions.
    path(
        "questions/<int:question_id>/edit/",
        views.edit_question,
        name="edit_question"
    ),

    path(
        "questions/<int:question_id>/delete/",
        views.delete_question,
        name="delete_question"
    ),

    # Submit answers and replies.
    path(
        "questions/<int:question_id>/answers/",
        views.submit_answer,
        name="submit_answer"
    ),

    # Edit and delete answers.
    path(
        "answers/<int:answer_id>/edit/",
        views.edit_answer,
        name="edit_answer"
    ),

    path(
        "answers/<int:answer_id>/delete/",
        views.delete_answer,
        name="delete_answer"
    ),

    # Resolve questions.
    path(
        "questions/<int:question_id>/resolve/",
        views.resolve_question,
        name="resolve_question"
    ),

    # Administrator moderation.
    path(
        "questions/<int:question_id>/moderate/",
        views.moderate_question,
        name="moderate_question"
    ),

    path(
        "answers/<int:answer_id>/moderate/",
        views.moderate_answer,
        name="moderate_answer"
    ),

]