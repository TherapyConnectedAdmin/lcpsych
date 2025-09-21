from django.contrib import admin
from .models import TherapistProfile


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "is_published", "accepts_new_clients")
    list_filter = ("is_published", "accepts_new_clients", "telehealth_only")
    search_fields = ("display_name", "user__username", "user__email", "licenses", "specialties", "modalities")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("display_name",)}
