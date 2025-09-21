from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Title(models.Model):
    name = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=48, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self) -> str:
        return self.name


class SpecialtyLookup(models.Model):
    name = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=48, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class TherapyType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=48, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class InsuranceProvider(models.Model):
    name = models.CharField(max_length=256, unique=True)
    category = models.CharField(max_length=48, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField(max_length=128, unique=True)
    category = models.CharField(max_length=48, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class ParticipantType(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self) -> str:
        return self.name


class AgeGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self) -> str:
        return self.name


class TherapistProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="therapist_profile")
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    # Core identity
    display_name = models.CharField(max_length=120)
    title = models.CharField(max_length=120, blank=True)
    title_fk = models.ForeignKey(Title, on_delete=models.SET_NULL, blank=True, null=True, related_name="therapists")
    first_name = models.CharField(max_length=64, blank=True, default="")
    last_name = models.CharField(max_length=64, blank=True, default="")
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, blank=True, null=True, related_name="therapists")
    photo = models.ImageField(upload_to="therapists/photos/", blank=True, null=True)

    # Professional details
    licenses = models.CharField(max_length=255, blank=True, help_text="Comma-separated license acronyms, e.g., LCSW, LMFT")
    npi_number = models.CharField(max_length=20, blank=True)
    specialties = models.TextField(blank=True, help_text="Comma-separated specialties (quick MVP)")
    modalities = models.TextField(blank=True, help_text="Comma-separated modalities (quick MVP)")

    # Content
    bio_html = models.TextField(blank=True)
    intro_statement = models.TextField(blank=True)
    practice_name = models.CharField(max_length=128, blank=True)
    practice_website_url = models.CharField(max_length=256, blank=True)
    facebook_url = models.CharField(max_length=256, blank=True)
    instagram_url = models.CharField(max_length=256, blank=True)
    linkedin_url = models.CharField(max_length=256, blank=True)

    # Contact/availability
    accepts_new_clients = models.BooleanField(default=True)
    telehealth_only = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    office_email = models.EmailField(max_length=128, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=64, blank=True)
    participant_types = models.ManyToManyField(ParticipantType, related_name="therapists", blank=True)
    age_groups = models.ManyToManyField(AgeGroup, related_name="therapists", blank=True)

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


class Specialty(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="specialty_items")
    specialty = models.ForeignKey(SpecialtyLookup, on_delete=models.CASCADE, null=True, default=None)
    is_top_specialty = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.specialty)


class TherapyTypeSelection(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="types_of_therapy")
    therapy_type = models.ForeignKey(TherapyType, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.therapy_type.name


class Education(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="educations")
    school = models.CharField(max_length=128)
    degree_diploma = models.CharField(max_length=64)
    year_graduated = models.CharField(max_length=4)
    year_began_practice = models.CharField(max_length=4, blank=True)

    def __str__(self) -> str:
        return f"{self.degree_diploma} from {self.school}"


class Location(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="locations")
    practice_name = models.CharField(max_length=128, blank=True)
    street_address = models.CharField(max_length=128, blank=True)
    address_line_2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64, blank=True)
    state = models.CharField(max_length=32, blank=True)
    zip = models.CharField(max_length=16, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    hide_address_from_public = models.BooleanField(default=False)
    is_primary_address = models.BooleanField(default=False)
    by_appointment_only = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.practice_name} ({self.city}, {self.state})"


class LicenseType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=512, blank=True, default="")
    short_description = models.CharField(max_length=80, blank=True, default="")
    category = models.CharField(max_length=48, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class License(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="licenses_details")
    license_type = models.ForeignKey(LicenseType, on_delete=models.PROTECT, related_name="licenses")
    state = models.CharField(max_length=2, blank=True, help_text="Two-letter state code (e.g., CA)")
    license_number = models.CharField(max_length=64, blank=True)
    date_issued = models.DateField(blank=True, null=True)
    date_expires = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "License"
        verbose_name_plural = "Licenses"

    def __str__(self) -> str:
        ty = self.license_type.name if self.license_type_id else ""
        st = f"-{self.state}" if self.state else ""
        return f"{ty}{st} #{self.license_number}".strip()


class OfficeHour(models.Model):
    """Represents a single day's office hours for a specific location.
    Allows optional second interval (split shift) and flags for closed / by appointment.
    """
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="office_hours")
    # 0=Monday .. 6=Sunday
    weekday = models.PositiveSmallIntegerField(help_text="0=Mon .. 6=Sun", default=0)
    is_closed = models.BooleanField(default=False)
    by_appointment_only = models.BooleanField(default=False, help_text="Ignore times; display 'By appointment' if true")
    start_time_1 = models.TimeField(blank=True, null=True)
    end_time_1 = models.TimeField(blank=True, null=True)
    start_time_2 = models.TimeField(blank=True, null=True)
    end_time_2 = models.TimeField(blank=True, null=True)
    notes = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["location", "weekday"]
        unique_together = ("location", "weekday")

    def __str__(self) -> str:
        return f"{self.location.practice_name or 'Location'} day {self.weekday}"


# Identity lookups
class RaceEthnicity(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.name


class Faith(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.name


class LGBTQIA(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.name


class OtherIdentity(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.name


# Identity selections
class RaceEthnicitySelection(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="race_ethnicities")
    race_ethnicity = models.ForeignKey(RaceEthnicity, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.race_ethnicity.name


class FaithSelection(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="faiths")
    faith = models.ForeignKey(Faith, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.faith.name


class LGBTQIASelection(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="lgbtqia_identities")
    lgbtqia = models.ForeignKey(LGBTQIA, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.lgbtqia.name


class OtherIdentitySelection(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="other_identities")
    other_identity = models.ForeignKey(OtherIdentity, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.other_identity.name


# Testing & Evaluation
class TestingType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=48, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class TestingTypeSelection(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="testing_types")
    testing_type = models.ForeignKey(TestingType, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.testing_type.name


class AreasOfExpertise(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="areas_of_expertise")
    expertise = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.expertise


class AdditionalCredential(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="additional_credentials")
    CREDENTIAL_TYPE_CHOICES = [
        ("Membership", "Membership"),
        ("License", "License"),
        ("Certificate", "Certificate"),
        ("Degree/Diploma", "Degree/Diploma"),
    ]
    additional_credential_type = models.CharField(max_length=16, blank=True, choices=CREDENTIAL_TYPE_CHOICES, default="")
    organization_name = models.CharField(max_length=64)
    id_number = models.CharField(max_length=32, blank=True)
    year_issued = models.CharField(max_length=4)

    def __str__(self) -> str:
        return f"{self.organization_name} ({self.id_number})"


class GalleryImage(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="therapists/gallery/")
    caption = models.CharField(max_length=128, blank=True)
    image_meta = models.JSONField(blank=True, null=True, default=dict)
    is_primary = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.caption or str(self.image)


class PaymentMethodSelection(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="accepted_payment_methods")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.payment_method.name


class InsuranceDetail(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="insurance_details")
    provider = models.ForeignKey(InsuranceProvider, on_delete=models.SET_NULL, null=True, blank=True)
    out_of_network = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.provider} ({'OON' if self.out_of_network else 'In-Network'})"


class VideoGallery(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="video_gallery")
    video = models.FileField(upload_to="therapists/video_gallery/")
    caption = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.caption or str(self.video)


class Credential(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="credentials")
    license_type = models.ForeignKey(LicenseType, on_delete=models.CASCADE, related_name="credentials", null=True, blank=True)

    def __str__(self) -> str:
        return str(self.license_type)


class ProfessionalInsurance(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="professional_insurances")
    npi_number = models.CharField(max_length=10, blank=True, unique=True)
    malpractice_carrier = models.CharField(max_length=64, blank=True)
    malpractice_expiration_date = models.CharField(max_length=7, blank=True)

    def __str__(self) -> str:
        return self.npi_number


class LicenseVerificationLog(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="license_verification_logs")
    status = models.CharField(max_length=32)
    message = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    raw = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self) -> str:
        return f"{self.therapist_id} {self.status} {self.created_at:%Y-%m-%d}"


class StateLicenseBoard(models.Model):
    state = models.CharField(max_length=2, db_index=True)
    board_name = models.CharField(max_length=128, blank=True)
    license_type = models.CharField(max_length=64, blank=True, help_text="Optional license type scope if board differs by type")
    search_url = models.CharField(max_length=512, help_text="Public search or lookup URL for manual + automated verification")
    active = models.BooleanField(default=True)
    notes = models.CharField(max_length=512, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("state", "license_type", "search_url")
        ordering = ["state", "license_type"]

    def __str__(self) -> str:
        return f"{self.state} {self.license_type or ''} board".strip()


class ZipCode(models.Model):
    zip = models.CharField(max_length=5, primary_key=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=2, db_index=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)

    def __str__(self) -> str:
        return f"{self.zip} ({self.city}, {self.state})"


class OtherTherapyType(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="other_therapy_types")
    therapy_type = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.therapy_type


class OtherTreatmentOption(models.Model):
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="other_treatment_options")
    option_text = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.option_text