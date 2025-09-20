from django.db import migrations, models
import django.db.models.deletion


def seed_services(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    Page = apps.get_model('core', 'Page')

    seeds = [
        {
            "title": "Evaluations",
            "slug": "evaluations",
            "excerpt": "Comprehensive ADHD and learning evaluations with testing and feedback.",
            "image_url": "/static/media/standardized-test-exams-form-with-answers-bubbled-in-and-color-pencil-resting-on-the-paper-test-education-concept-stockpack-adobe-stock.webp",
            "page_path": "services/evaluations",
            "order": 10,
        },
        {
            "title": "Parenting Support",
            "slug": "parenting-support",
            "excerpt": "Guidance for navigating the ever‑changing parent–child relationship.",
            "image_url": "/static/media/mom-and-her-son-hugging-each-other-mom-is-kissing-her-kid-in-the-forehead-stockpack-adobe-stock.webp",
            "page_path": "services/parenting-support",
            "order": 20,
        },
        {
            "title": "Couples Therapy",
            "slug": "couples-therapy",
            "excerpt": "Work together with a therapist to reconnect and move past sticking points.",
            "image_url": "/static/media/couple-looking-to-each-other-during-therapy-session-stockpack-adobe-stock.webp",
            "page_path": "services/couples-therapy",
            "order": 30,
        },
        {
            "title": "Family Therapy",
            "slug": "family-therapy",
            "excerpt": "Identify patterns and build healthier ways to connect as a family.",
            "image_url": "/static/media/parents-children-and-psychology-with-family-therapy-smile-and-together-on-sofa-support-and-discussion-young-kids-mom-and-dad-on-couch-with-psychologist-listening-and-talking-for-mental-health-stockpack-adobe-stock.webp",
            "page_path": "services/family-therapy",
            "order": 40,
        },
        {
            "title": "Individual Therapy",
            "slug": "individual-therapy",
            "excerpt": "One‑on‑one therapy focused on your personal goals and growth.",
            "image_url": "/static/media/psychotherapy-session-woman-talking-to-his-psychologist-in-the-studio-stockpack-adobe-stock.webp",
            "page_path": "services/individual-therapy",
            "order": 50,
        },
    ]

    for idx, data in enumerate(seeds):
        try:
            page = Page.objects.get(path=data["page_path"])
        except Page.DoesNotExist:
            continue
        Service.objects.update_or_create(
            slug=data["slug"],
            defaults={
                "title": data["title"],
                "excerpt": data["excerpt"],
                "image_url": data["image_url"],
                "page": page,
                "order": data["order"],
                "status": "publish",
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_services_pages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('excerpt', models.CharField(blank=True, max_length=500)),
                ('image_url', models.URLField(max_length=1000, blank=True, help_text='Absolute or /static relative URL for card background/image')),
                ('order', models.PositiveIntegerField(default=0, help_text='Controls display ordering on homepage')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('publish', 'Published')], default='publish', max_length=50)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_cards', to='core.page')),
            ],
            options={
                'ordering': ['order', 'title'],
            },
        ),
        migrations.RunPython(seed_services, migrations.RunPython.noop),
    ]
