from django.urls import path
from . import views

urlpatterns = [

    # Homepage
    path(
        "",
        views.home,
        name="home"
    ),

    # All Trainings
    path(
        "our-trainings/",
        views.training_list,
        name="training_list"
    ),

    # Courses under a particular category
    path(
    "our-trainings/category/<slug:slug>/",
    views.category_courses,
    name="category_courses"
),

    # Individual Course Details
    path(
        "courses/<slug:slug>/",
        views.course_detail,
        name="course_detail"
    ),

    # Lesson Video
    path(
        "lesson-video/<int:lesson_id>/",
        views.lesson_video_file,
        name="lesson_video_file"
    ),

    # Instructor creates lesson
    path(
        "instructor/modules/<int:module_id>/lessons/create/",
        views.create_lesson,
        name="create_lesson"
    ),


    path(
    "lesson-progress/<int:lesson_id>/save/",
    views.save_lesson_progress,
    name="save_lesson_progress"
),

# Advertisement Details
path(
    "advertisements/<int:pk>/",
    views.advertisement_detail,
    name="advertisement_detail"
),



# Student Lesson Notes
path(
    "lesson-notes/<int:lesson_id>/",
    views.lesson_notes,
    name="lesson_notes"
),

# Student Lesson Bookmarks
path(
    "lesson-bookmark/<int:lesson_id>/",
    views.lesson_bookmark,
    name="lesson_bookmark"
),
]