from django.contrib import admin
from .models import (
    TherapistProfile,
    Title,
    Gender,
    RaceEthnicity,
    Faith,
    LGBTQIA,
    OtherIdentity,
    RaceEthnicitySelection,
    FaithSelection,
    LGBTQIASelection,
    OtherIdentitySelection,
    SpecialtyLookup,
    TherapyType,
    TestingType,
    InsuranceProvider,
    PaymentMethod,
    ParticipantType,
    AgeGroup,
    Specialty,
    TherapyTypeSelection,
    TestingTypeSelection,
    AreasOfExpertise,
    Education,
    Location,
    LicenseType,
    License,
    OfficeHour,
    VideoGallery,
    Credential,
    AdditionalCredential,
    GalleryImage,
    PaymentMethodSelection,
    InsuranceDetail,
    ProfessionalInsurance,
    LicenseVerificationLog,
    StateLicenseBoard,
    ZipCode,
    OtherTherapyType,
    OtherTreatmentOption,
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
    fields = ("weekday", "is_closed", "by_appointment_only", "start_time_1", "end_time_1", "start_time_2", "end_time_2", "notes")


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
    list_display = ("therapist", "caption", "is_primary")
    list_filter = ("is_primary",)
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


@admin.register(RaceEthnicity)
class RaceEthnicityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Faith)
class FaithAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(LGBTQIA)
class LGBTQIAAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(OtherIdentity)
class OtherIdentityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(RaceEthnicitySelection)
class RaceEthnicitySelectionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "race_ethnicity")
    search_fields = ("therapist__display_name", "race_ethnicity__name")


@admin.register(FaithSelection)
class FaithSelectionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "faith")
    search_fields = ("therapist__display_name", "faith__name")


@admin.register(LGBTQIASelection)
class LGBTQIASelectionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "lgbtqia")
    search_fields = ("therapist__display_name", "lgbtqia__name")


@admin.register(OtherIdentitySelection)
class OtherIdentitySelectionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "other_identity")
    search_fields = ("therapist__display_name", "other_identity__name")


@admin.register(TestingType)
class TestingTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_editable = ("category", "sort_order")
    search_fields = ("name",)


@admin.register(TestingTypeSelection)
class TestingTypeSelectionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "testing_type")
    search_fields = ("therapist__display_name", "testing_type__name")


@admin.register(AreasOfExpertise)
class AreasOfExpertiseAdmin(admin.ModelAdmin):
    list_display = ("therapist", "expertise")
    search_fields = ("therapist__display_name", "expertise")


@admin.register(VideoGallery)
class VideoGalleryAdmin(admin.ModelAdmin):
    list_display = ("therapist", "caption")
    search_fields = ("therapist__display_name", "caption")


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ("therapist", "license_type")
    list_filter = ("license_type",)
    search_fields = ("therapist__display_name", "license_type__name")


@admin.register(ProfessionalInsurance)
class ProfessionalInsuranceAdmin(admin.ModelAdmin):
    list_display = ("therapist", "npi_number", "malpractice_carrier", "malpractice_expiration_date")
    search_fields = ("therapist__display_name", "npi_number", "malpractice_carrier")


@admin.register(LicenseVerificationLog)
class LicenseVerificationLogAdmin(admin.ModelAdmin):
    list_display = ("therapist", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("therapist__display_name", "status", "message")


@admin.register(StateLicenseBoard)
class StateLicenseBoardAdmin(admin.ModelAdmin):
    list_display = ("state", "board_name", "license_type", "active", "updated_at")
    list_filter = ("state", "active")
    search_fields = ("state", "board_name", "license_type")


@admin.register(ZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ("zip", "city", "state")
    list_filter = ("state",)
    search_fields = ("zip", "city", "state")


@admin.register(OtherTherapyType)
class OtherTherapyTypeAdmin(admin.ModelAdmin):
    list_display = ("therapist", "therapy_type")
    search_fields = ("therapist__display_name", "therapy_type")


@admin.register(OtherTreatmentOption)
class OtherTreatmentOptionAdmin(admin.ModelAdmin):
    list_display = ("therapist", "option_text")
    search_fields = ("therapist__display_name", "option_text")
