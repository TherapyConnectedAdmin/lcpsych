from django import forms
from .models import TherapistProfile


class TherapistProfileForm(forms.ModelForm):
    class Meta:
        model = TherapistProfile
        fields = [
            "display_name",
            "title",
            "photo",
            "licenses",
            "npi_number",
            "specialties",
            "modalities",
            "bio_html",
            "accepts_new_clients",
            "telehealth_only",
            "city",
            "state",
        ]
        widgets = {
            "bio_html": forms.Textarea(attrs={"rows": 8}),
        }
