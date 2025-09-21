from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TherapistProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="therapist_profile")
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    # Core identity
    display_name = models.CharField(max_length=120)
    title = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(upload_to="therapists/photos/", blank=True, null=True)

    # Professional details
    licenses = models.CharField(max_length=255, blank=True, help_text="Comma-separated license acronyms, e.g., LCSW, LMFT")
    npi_number = models.CharField(max_length=20, blank=True)
    specialties = models.TextField(blank=True, help_text="Comma-separated specialties (quick MVP)")
    modalities = models.TextField(blank=True, help_text="Comma-separated modalities (quick MVP)")

    # Content
    bio_html = models.TextField(blank=True)

    # Contact/availability
    accepts_new_clients = models.BooleanField(default=True)
    telehealth_only = models.BooleanField(default=False)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=64, blank=True)

    # Publishing
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name or self.user.get_username()

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.display_name or self.user.get_username())
            slug = base
            i = 2
            while TherapistProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)