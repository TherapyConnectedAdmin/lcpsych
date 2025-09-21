from django import forms
from .models import TherapistProfile


class TherapistProfileForm(forms.ModelForm):
    class Meta:
        model = TherapistProfile
        fields = [
            "display_name",
            "first_name",
            "last_name",
            "title",
            "title_fk",
            "gender",
            "photo",
            "licenses",
            "npi_number",
            "specialties",
            "modalities",
            "bio_html",
            "intro_statement",
            "practice_name",
            "practice_website_url",
            "facebook_url",
            "instagram_url",
            "linkedin_url",
            "accepts_new_clients",
            "telehealth_only",
            "phone_number",
            "office_email",
            "city",
            "state",
        ]
        widgets = {
            "bio_html": forms.Textarea(attrs={"rows": 8}),
            "intro_statement": forms.Textarea(attrs={"rows": 4}),
        }
