from rest_framework import serializers

from .models import Category, Course, Advertisement


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
        ]


class CourseSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Course

        fields = [
            "id",
            "title",
            "slug",
            "description",
            "level",
            "thumbnail",
            "category_name",
            "instructor_name",
        ]

    def get_instructor_name(self, obj):
        return str(obj.instructor)


class AdvertisementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advertisement

        fields = [
            "id",
            "title",
            "description",
            "image",
            "target_url",
            "placement",
        ]