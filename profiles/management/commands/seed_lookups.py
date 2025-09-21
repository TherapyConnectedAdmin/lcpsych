from django.core.management.base import BaseCommand
from django.db import transaction

from profiles.models import (
    Title,
    Gender,
    ParticipantType,
    AgeGroup,
    PaymentMethod,
    InsuranceProvider,
    TherapyType,
    SpecialtyLookup,
)


class Command(BaseCommand):
    help = "Seed lookup tables for therapist profiles (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument('--purge-extra', action='store_true', help='Purge non-canonical rows for supported models (safe subset).')

    @transaction.atomic
    def handle(self, *args, **opts):
        created_total = 0
        updated_total = 0

        def _getset(model, name, category=None, sort_order=None):
            nonlocal created_total, updated_total
            obj, created = model.objects.get_or_create(name=name)
            changed = False
            if category is not None and getattr(obj, 'category', '') != category:
                try:
                    obj.category = category
                    changed = True
                except Exception:
                    pass
            if sort_order is not None and getattr(obj, 'sort_order', 0) != sort_order:
                try:
                    obj.sort_order = sort_order
                    changed = True
                except Exception:
                    pass
            if changed:
                obj.save()
                updated_total += 1
            if created:
                created_total += 1
            return obj

        # Participant Types
        pt_vals = ["Individual", "Couple", "Family", "Group"]
        for i, name in enumerate(pt_vals, start=1):
            _getset(ParticipantType, name, sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(pt_vals)} participant types."))

        # Age Groups (normalized labels)
        ag_vals = [
            "Children (0-5)",
            "Children (6-10)",
            "Preteens (11-12)",
            "Teens (13-17)",
            "Young Adults (18-25)",
            "Adults (26-64)",
            "Older Adults (65+)",
        ]
        for i, name in enumerate(ag_vals, start=1):
            _getset(AgeGroup, name, sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(ag_vals)} age groups."))

        # Gender
        for i, name in enumerate(["Male", "Female"], start=1):
            _getset(Gender, name, sort_order=i)
        self.stdout.write(self.style.SUCCESS("Seeded gender values."))

        # Titles
        titles = [
            "Dr.", "Mr.", "Ms.", "Mx.", "Prof.", "Rev.", "Rev. Dr.", "Rabbi", "Pastor", "Father", "Sister",
        ]
        for i, name in enumerate(titles, start=1):
            _getset(Title, name, sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(titles)} titles."))

        # Payment Methods (with categories)
        pm_vals = [
            ("Cash", "Cash"),
            ("Check", "Cash"),
            ("Visa", "Card"),
            ("Mastercard", "Card"),
            ("American Express", "Card"),
            ("Discover", "Card"),
            ("Debit Card", "Card"),
            ("HSA Card", "Health Account"),
            ("FSA Card", "Health Account"),
            ("ACH Transfer", "Bank"),
            ("Wire Transfer", "Bank"),
            ("Apple Pay", "Digital Wallet"),
            ("Google Pay", "Digital Wallet"),
            ("PayPal", "Digital Wallet"),
            ("Venmo", "Peer-to-Peer"),
            ("Zelle", "Peer-to-Peer"),
        ]
        for i, (name, cat) in enumerate(pm_vals, start=1):
            _getset(PaymentMethod, name, category=cat, sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(pm_vals)} payment methods."))

        # Insurance Providers (concise core set)
        ins_vals = [
            ("Aetna", "Commercial"),
            ("Anthem Blue Cross Blue Shield", "Commercial"),
            ("Blue Cross Blue Shield (BCBS)", "Commercial"),
            ("Cigna (Evernorth)", "Commercial"),
            ("UnitedHealthcare / Optum", "Commercial"),
            ("Humana", "Commercial"),
            ("Kaiser Permanente", "Commercial"),
            ("Molina Healthcare", "Commercial"),
            ("Oscar Health", "Commercial"),
            ("Oxford (UHC)", "Commercial"),
            ("Medicare", "Government"),
            ("Medicaid", "Government"),
            ("TRICARE", "Government"),
            ("TriWest", "Government"),
            ("Self-Pay / Private Pay", "Other"),
        ]
        for i, (name, cat) in enumerate(ins_vals, start=1):
            _getset(InsuranceProvider, name, category=cat, sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(ins_vals)} insurance providers."))

        # Therapy Types (core evidence-based + relational + adjunct subset)
        tt_vals = [
            "Acceptance & Commitment Therapy (ACT)",
            "Cognitive Behavioral Therapy (CBT)",
            "Dialectical Behavior Therapy (DBT)",
            "Exposure & Response Prevention (ERP)",
            "Mindfulness-Based Cognitive Therapy (MBCT)",
            "Eye Movement Desensitization & Reprocessing (EMDR)",
            "Schema Therapy",
            "Solution Focused Brief Therapy (SFBT)",
            "Internal Family Systems (IFS)",
            "Somatic Therapy",
            "Attachment-Based",
            "Brainspotting",
            "Trauma Focused",
            "Psychodynamic",
            "Psychoanalytic",
            "Jungian",
            "Marriage & Family Therapy",
            "Gottman Method",
            "Emotionally Focused Therapy (EFT)",
            "Imago Relationship Therapy",
            "Humanistic",
            "Person-Centered",
            "Gestalt",
            "Existential",
            "Transpersonal",
            "Multicultural",
            "Culturally Sensitive",
            "Strength-Based",
            "Integrative",
            "Eclectic",
            "Mindfulness-Based Stress Reduction (MBSR)",
            "Compassion Focused",
            "Positive Psychology",
            "Narrative Therapy",
            "Motivational Interviewing",
            "Rational Emotive Behavior Therapy (REBT)",
            "Reality Therapy",
            "Play Therapy",
            "Neurofeedback",
            "Biofeedback",
            "Hypnotherapy",
        ]
        # Basic categorization for future UI groupings
        def tt_category(name: str) -> str:
            low = name.lower()
            if any(k in low for k in ["trauma", "somatic", "brainspot", "emdr"]):
                return "Trauma / Somatic"
            if any(k in low for k in ["ifs", "internal family"]):
                return "Parts / Internal"
            if any(k in low for k in ["mindfulness", "acceptance", "dialectical", "mbct", "act", "dbt"]):
                return "Mindfulness / Third Wave"
            if any(k in low for k in ["cbt", "exposure", "solution", "schema", "rebt", "reality"]):
                return "CBT / Structured"
            if any(k in low for k in ["family", "gottman", "eft", "imago", "marriage"]):
                return "Family / Couples"
            if any(k in low for k in ["humanistic", "gestalt", "experiential", "existential", "transpersonal", "person-centered"]):
                return "Humanistic / Experiential"
            if any(k in low for k in ["psychodynamic", "psychoanalytic", "jungian"]):
                return "Psychodynamic / Analytic"
            if any(k in low for k in ["integrative", "eclectic", "strength", "multicultural", "culturally"]):
                return "Integrative / Identity"
            if any(k in low for k in ["narrative", "motivational", "positive"]):
                return "Constructivist / Change"
            if any(k in low for k in ["biofeedback", "hypno", "neurofeedback"]):
                return "Adjunct / Specialized"
            return "Other"

        for i, name in enumerate(tt_vals, start=1):
            _getset(TherapyType, name, category=tt_category(name), sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(tt_vals)} therapy types."))

        # Specialty Lookup (curated subset)
        spec_vals = [
            "Depression", "Anxiety", "Obsessive-Compulsive (OCD)", "Trauma and PTSD", "Stress",
            "Panic / Agoraphobia", "Borderline Personality Disorder (BPD)",
            "Autism", "ADHD", "Learning Disabilities",
            "Chronic Illness", "Sleep or Insomnia",
            "Relationship Issues", "Marital and Premarital", "Family Conflict", "Divorce",
            "Women's Issues", "Men's Issues", "LGBTQ+",
            "Sex Therapy", "Grief", "Self Esteem", "Life Transitions", "Career Counseling",
            "Eating Disorders", "Substance Use Disorder", "Alcohol Use Disorder", "Gambling",
        ]

        def spec_category(name: str) -> str:
            low = name.lower()
            if any(k in low for k in ["depress", "anxiety", "ocd", "panic", "mood"]):
                return "Mood / Anxiety"
            if any(k in low for k in ["trauma", "ptsd", "stress"]):
                return "Trauma / Stressor"
            if any(k in low for k in ["adhd", "autism", "neuro", "learning", "intellectual", "hoard"]):
                return "Neurodevelopmental"
            if any(k in low for k in ["sleep", "chronic", "cancer", "weight", "medical"]):
                return "Health / Medical"
            if any(k in low for k in ["relationship", "marital", "family", "divorce"]):
                return "Relationships / Family"
            if any(k in low for k in ["women", "men", "lgbtq", "gender", "racial", "veteran", "first responder"]):
                return "Population / Identity"
            if any(k in low for k in ["grief", "esteem", "career", "transition", "coping", "social"]):
                return "Skills / Adjustment"
            if any(k in low for k in ["eating", "body"]):
                return "Body / Self Image"
            if any(k in low for k in ["substance", "alcohol", "gambling", "addiction"]):
                return "Substance / Addictive"
            return "Other"

        for i, name in enumerate(spec_vals, start=1):
            _getset(SpecialtyLookup, name, category=spec_category(name), sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(spec_vals)} specialty lookups."))

        # Optional purge (safe subset only)
        if opts.get('purge_extra'):
            # For these models, we can safely remove rows not in the canonical lists
            def _purge(model, keep_names, label):
                qs = model.objects.exclude(name__in=set(keep_names))
                count = qs.count()
                if count:
                    qs.delete()
                self.stdout.write(self.style.WARNING(f"Purged {count} extra rows from {label}."))

            _purge(ParticipantType, pt_vals, 'ParticipantType')
            _purge(AgeGroup, ag_vals, 'AgeGroup')
            _purge(Gender, ["Male", "Female"], 'Gender')
            _purge(Title, titles, 'Title')
            _purge(PaymentMethod, [n for n, _ in pm_vals], 'PaymentMethod')
            _purge(InsuranceProvider, [n for n, _ in ins_vals], 'InsuranceProvider')
            _purge(TherapyType, tt_vals, 'TherapyType')
            _purge(SpecialtyLookup, spec_vals, 'SpecialtyLookup')

        self.stdout.write(self.style.SUCCESS(f"Lookup seed complete. created={created_total} updated={updated_total}"))
