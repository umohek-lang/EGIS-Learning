from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from courses.models import Course
from .models import SubscriptionPlan


@login_required
def plan_list(request, course_slug):

    course = get_object_or_404(
        Course,
        slug=course_slug,
        is_published=True,
        category__is_active=True,
    )

    plans = SubscriptionPlan.objects.filter(
        course=course,
        is_active=True,
    ).order_by("duration_months")

    return render(
        request,
        "subscriptions/plans.html",
        {
            "course": course,
            "plans": plans,
        },
    )