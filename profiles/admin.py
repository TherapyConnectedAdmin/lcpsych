from django.contrib import admin
from .models import (
    TherapistProfile,
    Title,
    Gender,
    SpecialtyLookup,
    TherapyType,
    InsuranceProvider,
    PaymentMethod,
    ParticipantType,
    AgeGroup,
    Specialty,
    TherapyTypeSelection,
    Education,
    Location,
    LicenseType,
    License,
    OfficeHour,
    AdditionalCredential,
    GalleryImage,
    PaymentMethodSelection,
    InsuranceDetail,
)


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "is_published", "accepts_new_clients")
    list_filter = ("is_published", "accepts_new_clients", "telehealth_only", "gender", "title_fk")
    search_fields = (
        "display_name",
        "first_name",
        "last_name",
        "user__username",
        "user__email",
        "licenses",
        "specialties",
        "modalities",
    )
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("display_name",)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_editable = ("category", "sort_order")
    search_fields = ("name",)


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(SpecialtyLookup)
class SpecialtyLookupAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_editable = ("category", "sort_order")
    search_fields = ("name",)


@admin.register(TherapyType)
class TherapyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_editable = ("category", "sort_order")
    search_fields = ("name",)


@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_editable = ("category", "sort_order")
    search_fields = ("name",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_editable = ("category", "sort_order")
    search_fields = ("name",)


@admin.register(ParticipantType)
class ParticipantTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("therapist", "specialty", "is_top_specialty")
    list_filter = ("is_top_specialty",)
    search_fields = ("therapist__display_name", "specialty__name")


@admin.register(TherapyTypeSelection)
class TherapyTypeSelectionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "therapy_type")
    search_fields = ("therapist__display_name", "therapy_type__name")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("therapist", "school", "degree_diploma", "year_graduated")
    search_fields = ("therapist__display_name", "school", "degree_diploma")


class OfficeHourInline(admin.TabularInline):
    model = OfficeHour
    extra = 0
    fields = ("day_of_week", "start_time", "end_time", "is_closed", "notes")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("therapist", "practice_name", "city", "state", "zip", "is_primary_address", "by_appointment_only")
    list_filter = ("state", "is_primary_address", "by_appointment_only")
    search_fields = ("therapist__display_name", "practice_name", "city", "state", "zip")
    inlines = [OfficeHourInline]


@admin.register(AdditionalCredential)
class AdditionalCredentialAdmin(admin.ModelAdmin):
    list_display = ("therapist", "additional_credential_type", "organization_name", "year_issued")
    list_filter = ("additional_credential_type",)
    search_fields = ("therapist__display_name", "organization_name")


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("therapist", "caption")
    search_fields = ("therapist__display_name", "caption")


@admin.register(PaymentMethodSelection)
class PaymentMethodSelectionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "payment_method")
    search_fields = ("therapist__display_name", "payment_method__name")


@admin.register(InsuranceDetail)
class InsuranceDetailAdmin(admin.ModelAdmin):
    list_display = ("therapist", "provider", "out_of_network")
    list_filter = ("out_of_network",)
    search_fields = ("therapist__display_name", "provider__name")


class LicenseInline(admin.TabularInline):
    model = License
    extra = 0
    fields = ("license_type", "state", "license_number", "date_issued", "date_expires", "is_active")


@admin.register(LicenseType)
class LicenseTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_editable = ("category", "sort_order")
    search_fields = ("name",)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("therapist", "license_type", "state", "license_number", "date_expires", "is_active")
    list_filter = ("license_type", "state", "is_active")
    search_fields = ("therapist__display_name", "license_number", "license_type__name")
