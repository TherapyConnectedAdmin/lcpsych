from urllib.parse import urlparse
from django.conf import settings
from .models import NavItem


def nav(request):
    items = list(NavItem.objects.select_related('parent').order_by('order', 'title'))
    roots = [i for i in items if not i.parent]
    current_path = request.path.rstrip('/') or '/'
    host = request.get_host()
    same_site_hosts = {host, '', 'www.lcpsych.com', 'lcpsych.com'}
    tree = []
    for r in roots:
        r_url = r.url or '/'
        parsed = urlparse(r_url)
        path_only = parsed.path or '/'
        is_same_host = parsed.netloc in same_site_hosts
        # Convert same-site home anchors to local in-page anchors for SPA-like behavior
        if is_same_host and (path_only in ('', '/')) and parsed.fragment:
            display_url = f"#{parsed.fragment}"
            is_external = False
        elif is_same_host:
            # Keep path + fragment for internal links
            display_url = path_only + (f"#{parsed.fragment}" if parsed.fragment else '')
            is_external = False
        else:
            display_url = r_url
            is_external = r.is_external

        active = is_same_host and (current_path == (path_only.rstrip('/') or '/'))
        children = [c for c in items if c.parent_id == r.id]
        tree.append({
            'title': r.title,
            'url': display_url,
            'is_external': is_external,
            'active': active,
            'children': [{'title': c.title, 'url': c.url, 'is_external': c.is_external} for c in children],
        })
    return {'nav_items': tree}


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
    }
