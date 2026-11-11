from django.utils import timezone
from django.db.models import Q

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Course, Advertisement

from .serializers import (
    CategorySerializer,
    CourseSerializer,
    AdvertisementSerializer,
)


@api_view(["GET"])
def homepage_api(request):

    now = timezone.now()

    # Get active categories
    categories = Category.objects.filter(
        is_active=True
    )

    # Get published courses
    courses = Course.objects.filter(
        is_published=True,
        category__is_active=True,
    ).select_related(
        "category",
        "instructor",
    )

    # Get currently active homepage advertisements
    advertisements = Advertisement.objects.filter(
        is_active=True,
        placement=Advertisement.Placement.HOMEPAGE,
    ).filter(
        Q(start_at__isnull=True) |
        Q(start_at__lte=now)
    ).filter(
        Q(end_at__isnull=True) |
        Q(end_at__gt=now)
    )

    # Serialize database information
    category_data = CategorySerializer(
        categories,
        many=True,
        context={"request": request}
    )

    course_data = CourseSerializer(
        courses,
        many=True,
        context={"request": request}
    )

    advertisement_data = AdvertisementSerializer(
        advertisements,
        many=True,
        context={"request": request}
    )

    # Return JSON response to React
    return Response({

        "categories": category_data.data,

        "courses": course_data.data,

        "advertisements": advertisement_data.data,

    })