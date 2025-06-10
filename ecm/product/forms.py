from django import forms
from .models import Review

from django.core.exceptions import ValidationError

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image', 'video']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'video': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
        }

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if not video.content_type.startswith('video/'):
                raise ValidationError("Uploaded file is not a valid video.")
        return video
