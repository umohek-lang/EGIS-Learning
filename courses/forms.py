
from pathlib import Path

from django import forms

from .models import Lesson


MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "description",
            "video_file",
            "duration_minutes",
            "order",
            "is_free_preview",
            "is_published",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter lesson title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe what students will learn",
            }),
            "video_file": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": ".mp4,.webm,.mov,video/mp4,video/webm,video/quicktime",
            }),
            "duration_minutes": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
            }),
            "order": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
            }),
            "is_free_preview": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "is_published": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_video_file(self):
        video = self.cleaned_data.get("video_file")

        if not video:
            return video

        extension = Path(video.name).suffix.lower()

        if extension not in ALLOWED_VIDEO_EXTENSIONS:
            raise forms.ValidationError(
                "Upload an MP4, WebM, or MOV video file."
            )

        if video.size > MAX_VIDEO_SIZE:
            raise forms.ValidationError(
                "The video cannot exceed 500 MB."
            )

        return video
