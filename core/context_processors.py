from urllib.parse import urlparse
from django.conf import settings


def nav(request):
    """
    Deprecated NavItem-based navigation.
    Templates currently use static header markup, so nav_items is unused.
    Keep returning an empty list to avoid template KeyErrors and DB hits.
    """
    return {'nav_items': []}


def seo(request):
    """
    Provides default SEO context values that templates can override per page.
    - seo_title: <title>
    - seo_description: <meta name="description">
    - canonical_url: absolute canonical URL if BASE_URL is set
    - robots: meta robots content (e.g., index, follow)
    """
    # Sensible defaults matching the homepage copy
    default_title = "Mental Health Therapy in Northern Kentucky | L+C Psych"
    default_description = (
        "At L+C Psych our Psychologists, Therapists, and Counselors offer evaluations "
        "and therapy in Northern Kentucky and online throughout the state."
    )

    base_url = (getattr(settings, 'BASE_URL', '') or '').rstrip('/')
    # Compute site_base: prefer settings.BASE_URL, else from request
    if base_url:
        site_base = base_url
    else:
        # request.build_absolute_uri('/') returns 'https://host/'
        site_base = request.build_absolute_uri('/')[:-1]

    # Build canonical absolute URL
    canonical = f"{site_base}{request.path}"

    robots_allow = getattr(settings, 'ROBOTS_ALLOW', not settings.DEBUG)
    robots_value = 'index, follow' if robots_allow else 'noindex, nofollow'

    # Choose a default social image path that's in our static folder
    default_image_path = '/static/vendor/lcpsych/wp-content/uploads/2017/08/LC_logo_color.png'
    og_image_url = f"{site_base}{default_image_path}"

    sitemap_url = f"{site_base}/sitemap.xml"

    return {
        'seo_title': default_title,
        'seo_description': default_description,
        'canonical_url': canonical,
        'robots': robots_value,
        'site_base': site_base,
        'og_image_url': og_image_url,
        'sitemap_url': sitemap_url,
    'GOOGLE_SITE_VERIFICATION': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
    }
