from django.db import migrations
from django.utils.text import slugify
from datetime import datetime


SERVICES = [
    {
        "title": "Evaluations",
        "slug": "evaluations",
        "excerpt_html": "<p>Comprehensive evaluations for ADHD and learning differences, including testing, reporting, and feedback sessions.</p>",
        "content_html": """
          <h1>Evaluations</h1>
          <p>We offer comprehensive psychoeducational evaluations to assess for Attention Deficit Hyperactivity Disorder (ADHD) and Learning Disabilities. Our process includes interviews, standardized testing, integrated reporting, and a feedback session.</p>
          <p>We partner with parents, teachers, and caregivers to ensure a complete picture, and provide clear recommendations for school and home.</p>
          <p><strong>Next steps:</strong> Call us at <a href=\"tel:8595254911\">(859) 525-4911</a> or <a href=\"https://www.therapyportal.com/p/lcpsych41042/appointments/availability/\" target=\"_blank\" rel=\"noopener\">schedule online</a>.</p>
        """.strip(),
    },
    {
        "title": "Parenting Support",
        "slug": "parenting-support",
        "excerpt_html": "<p>Guidance and strategies to navigate the ever-changing relationship with your child.</p>",
        "content_html": """
          <h1>Parenting Support</h1>
          <p>Work with a therapist to build effective strategies, strengthen connection, and respond to challenging behaviors with confidence and compassion.</p>
          <p>We tailor our approach to your family’s values, routines, and goals.</p>
          <p><strong>Next steps:</strong> Call us at <a href=\"tel:8595254911\">(859) 525-4911</a> or <a href=\"https://www.therapyportal.com/p/lcpsych41042/appointments/availability/\" target=\"_blank\" rel=\"noopener\">schedule online</a>.</p>
        """.strip(),
    },
    {
        "title": "Couples Therapy",
        "slug": "couples-therapy",
        "excerpt_html": "<p>Therapy to rebuild trust, improve communication, and reconnect with your partner.</p>",
        "content_html": """
          <h1>Couples Therapy</h1>
          <p>We help couples identify stuck patterns, repair hurts, and develop tools for navigating conflict while staying emotionally connected.</p>
          <p>Whether you’re proactively investing in your relationship or working through a difficult season, we’ll meet you where you are.</p>
          <p><strong>Next steps:</strong> Call us at <a href=\"tel:8595254911\">(859) 525-4911</a> or <a href=\"https://www.therapyportal.com/p/lcpsych41042/appointments/availability/\" target=\"_blank\" rel=\"noopener\">schedule online</a>.</p>
        """.strip(),
    },
    {
        "title": "Family Therapy",
        "slug": "family-therapy",
        "excerpt_html": "<p>Collaborative therapy to create healthier patterns of interaction at home.</p>",
        "content_html": """
          <h1>Family Therapy</h1>
          <p>Together we’ll identify patterns that help or harm connection and develop new ways to support each family member’s needs while strengthening the whole.</p>
          <p>Sessions can include different combinations of family members as appropriate.</p>
          <p><strong>Next steps:</strong> Call us at <a href=\"tel:8595254911\">(859) 525-4911</a> or <a href=\"https://www.therapyportal.com/p/lcpsych41042/appointments/availability/\" target=\"_blank\" rel=\"noopener\">schedule online</a>.</p>
        """.strip(),
    },
    {
        "title": "Individual Therapy",
        "slug": "individual-therapy",
        "excerpt_html": "<p>One-on-one therapy to set goals, build skills, and improve wellbeing.</p>",
        "content_html": """
          <h1>Individual Therapy</h1>
          <p>Collaborate with a therapist to set meaningful goals and make progress at a sustainable pace. We integrate evidence-based approaches matched to your needs.</p>
          <p>Common focuses include anxiety, depression, life transitions, stress, and personal growth.</p>
          <p><strong>Next steps:</strong> Call us at <a href=\"tel:8595254911\">(859) 525-4911</a> or <a href=\"https://www.therapyportal.com/p/lcpsych41042/appointments/availability/\" target=\"_blank\" rel=\"noopener\">schedule online</a>.</p>
        """.strip(),
    },
]


def seed_services(apps, schema_editor):
    Page = apps.get_model('core', 'Page')

    # Ensure a Services index page exists at path 'services'
    services_page, _ = Page.objects.get_or_create(
        path='services',
        defaults={
            'title': 'Services',
            'slug': 'services',
            'excerpt_html': '<p>Explore our counseling and evaluation services. Each service page includes what to expect and how to get started.</p>',
            'content_html': '',
            'menu_order': 10,
            'status': 'publish',
            'wp_id': 900000,  # arbitrary but unique within wp_type
            'wp_type': 'page',
        }
    )

    # Seed child service pages
    next_wp_id = 900001
    for svc in SERVICES:
        slug = svc['slug'] or slugify(svc['title'])
        path = f"services/{slug}"
        Page.objects.get_or_create(
            path=path,
            defaults={
                'title': svc['title'],
                'slug': slug,
                'excerpt_html': svc.get('excerpt_html', ''),
                'content_html': svc.get('content_html', ''),
                'parent_id': services_page.id,
                'menu_order': 0,
                'status': 'publish',
                'wp_id': next_wp_id,
                'wp_type': 'page',
            }
        )
        next_wp_id += 1


def unseed_services(apps, schema_editor):
    Page = apps.get_model('core', 'Page')
    try:
        services_page = Page.objects.get(path='services')
    except Page.DoesNotExist:
        return
    # Delete children first, then parent
    Page.objects.filter(parent_id=services_page.id).delete()
    services_page.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_remove_navitem'),
    ]

    operations = [
        migrations.RunPython(seed_services, unseed_services),
    ]
