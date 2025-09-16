from urllib.parse import urlparse
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
