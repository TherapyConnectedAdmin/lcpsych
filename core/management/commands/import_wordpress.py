import datetime
from typing import Any, Dict, List, Optional

import requests
from defusedxml import ElementTree as ET
from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from django.utils.text import slugify

from core.models import Page, Post, Category, Tag


class Command(BaseCommand):
    help = "Import content from a WordPress REST API or a WXR file (REST implemented)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--site', type=str, help='WordPress site base URL for REST import, e.g. https://example.com')
        parser.add_argument('--wxr', type=str, help='Path to WordPress WXR (XML) export file')
        parser.add_argument('--per-page', type=int, default=100, help='Items per page to fetch from API')
        parser.add_argument('--posts', action='store_true', help='Import posts')
        parser.add_argument('--pages', action='store_true', help='Import pages')
        parser.add_argument('--tax', action='store_true', help='Import categories and tags')
        parser.add_argument('--truncate', action='store_true', help='Delete existing imported content first')

    def handle(self, *args, **options):
        site = (options.get('site') or '').rstrip('/')
        wxr = options.get('wxr')
        per_page = options['per_page']
        do_posts = options['posts']
        do_pages = options['pages']
        do_tax = options['tax']
        truncate = options['truncate']

        if not (do_posts or do_pages or do_tax):
            do_posts = do_pages = do_tax = True

        if truncate:
            Page.objects.all().delete()
            Post.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()

        if wxr:
            self._import_wxr(wxr, do_posts, do_pages, do_tax)
        elif site:
            if do_tax:
                self._import_taxonomies(site, per_page)
            if do_pages:
                self._import_pages(site, per_page)
            if do_posts:
                self._import_posts(site, per_page)
        else:
            raise SystemExit("Provide --site for REST or --wxr for file import")

        self.stdout.write(self.style.SUCCESS('Import complete.'))

    def _fetch_all(self, url: str, per_page: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        page = 1
        while True:
            r = requests.get(url, params={'per_page': per_page, 'page': page, '_embed': 'true'}, timeout=30)
            if r.status_code == 400 and 'rest_post_invalid_page_number' in r.text:
                break
            r.raise_for_status()
            batch = r.json()
            if not batch:
                break
            items.extend(batch)
            if len(batch) < per_page:
                break
            page += 1
        return items

    def _import_taxonomies(self, base: str, per_page: int):
        cats = self._fetch_all(f"{base}/wp-json/wp/v2/categories", per_page)
        for c in cats:
            obj, _ = Category.objects.update_or_create(
                wp_id=c['id'],
                defaults={
                    'name': c.get('name') or '',
                    'slug': c.get('slug') or slugify(c.get('name') or str(c['id'])),
                    'description': c.get('description') or '',
                }
            )
        tags = self._fetch_all(f"{base}/wp-json/wp/v2/tags", per_page)
        for t in tags:
            obj, _ = Tag.objects.update_or_create(
                wp_id=t['id'],
                defaults={
                    'name': t.get('name') or '',
                    'slug': t.get('slug') or slugify(t.get('name') or str(t['id'])),
                    'description': t.get('description') or '',
                }
            )

    def _import_pages(self, base: str, per_page: int):
        pages = self._fetch_all(f"{base}/wp-json/wp/v2/pages", per_page)
        cache: Dict[int, Page] = {}
        # First pass create pages without parents, second pass set parents
        for p in pages:
            page_obj = self._upsert_page(base, p, parent=None)
            cache[p['id']] = page_obj
        for p in pages:
            parent_id = p.get('parent')
            if parent_id:
                parent = cache.get(parent_id)
                if parent:
                    self._upsert_page(base, p, parent=parent)

    def _upsert_page(self, base: str, p: Dict[str, Any], parent: Optional[Page]) -> Page:
        from urllib.parse import urlparse
        slug = p.get('slug') or slugify(p.get('title', {}).get('rendered') or str(p['id']))
        link = p.get('link') or ''
        parsed = urlparse(link)
        # Use URL path regardless of host variations; root becomes ''
        path = (parsed.path or '/').strip('/') or ''
        if not path:
            path = ''  # homepage
        # Fallback to slug for odd cases with no path
        if path is None:
            path = slug
        published = self._parse_dt(p.get('date_gmt'))
        modified = self._parse_dt(p.get('modified_gmt'))
        obj, _ = Page.objects.update_or_create(
            wp_id=p['id'], wp_type='page',
            defaults={
                'title': (p.get('title') or {}).get('rendered') or '',
                'slug': slug[:255],
                'path': path,
                'excerpt_html': (p.get('excerpt') or {}).get('rendered') or '',
                'content_html': (p.get('content') or {}).get('rendered') or '',
                'menu_order': p.get('menu_order') or 0,
                'status': p.get('status') or 'publish',
                'original_url': p.get('link') or '',
                'published_at': published,
                'modified_at': modified,
                'parent': parent,
            }
        )
        return obj

    def _import_posts(self, base: str, per_page: int):
        posts = self._fetch_all(f"{base}/wp-json/wp/v2/posts", per_page)
        for p in posts:
            slug = p.get('slug') or slugify(p.get('title', {}).get('rendered') or str(p['id']))
            published = self._parse_dt(p.get('date_gmt'))
            modified = self._parse_dt(p.get('modified_gmt'))
            obj, _ = Post.objects.update_or_create(
                wp_id=p['id'], wp_type='post',
                defaults={
                    'title': (p.get('title') or {}).get('rendered') or '',
                    'slug': slug[:255],
                    'excerpt_html': (p.get('excerpt') or {}).get('rendered') or '',
                    'content_html': (p.get('content') or {}).get('rendered') or '',
                    'status': p.get('status') or 'publish',
                    'original_url': p.get('link') or '',
                    'published_at': published,
                    'modified_at': modified,
                }
            )
            # Categories/Tags relations
            cat_ids = p.get('categories') or []
            tag_ids = p.get('tags') or []
            if cat_ids:
                obj.categories.set(list(Category.objects.filter(wp_id__in=cat_ids)))
            if tag_ids:
                obj.tags.set(list(Tag.objects.filter(wp_id__in=tag_ids)))

    def _parse_dt(self, s: Optional[str]):
        if not s:
            return None
        try:
            return datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(timezone.utc)
        except Exception:
            return None

    def _import_wxr(self, path: str, do_posts: bool, do_pages: bool, do_tax: bool):
        ns = {
            'wp': 'http://wordpress.org/export/1.2/',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'dc': 'http://purl.org/dc/elements/1.1/',
        }
        tree = ET.parse(path)
        root = tree.getroot()
        channel = root.find('channel')
        if channel is None:
            return
        if do_tax:
            for cat in channel.findall('wp:category', ns):
                name = (cat.findtext('wp:cat_name', default='') or '').strip()
                slug = (cat.findtext('wp:category_nicename', default='') or '').strip()
                term_id = cat.findtext('wp:term_id')
                wp_id = int(term_id) if term_id and term_id.isdigit() else None
                if name:
                    Category.objects.update_or_create(
                        wp_id=wp_id,
                        defaults={'name': name, 'slug': slug or slugify(name)},
                    )
            for tag in channel.findall('wp:tag', ns):
                name = (tag.findtext('wp:tag_name', default='') or '').strip()
                slug = (tag.findtext('wp:tag_slug', default='') or '').strip()
                term_id = tag.findtext('wp:term_id')
                wp_id = int(term_id) if term_id and term_id.isdigit() else None
                if name:
                    Tag.objects.update_or_create(
                        wp_id=wp_id,
                        defaults={'name': name, 'slug': slug or slugify(name)},
                    )
        for item in channel.findall('item'):
            post_type = item.findtext('wp:post_type', default='', namespaces=ns)
            status = item.findtext('wp:status', default='publish', namespaces=ns)
            title = item.findtext('title', default='')
            link = item.findtext('link', default='')
            content_html = item.findtext('content:encoded', default='', namespaces=ns) or ''
            excerpt_html = item.findtext('excerpt:encoded', default='', namespaces=ns) or ''
            post_id_text = item.findtext('wp:post_id', default='', namespaces=ns)
            post_id = int(post_id_text) if post_id_text.isdigit() else None
            date = item.findtext('wp:post_date_gmt', default='', namespaces=ns) or None
            modified = item.findtext('wp:post_modified_gmt', default='', namespaces=ns) or None
            published_at = self._parse_dt(date)
            modified_at = self._parse_dt(modified)
            slug = item.findtext('wp:post_name', default='', namespaces=ns) or slugify(title)

            if post_type == 'page' and do_pages and post_id:
                Page.objects.update_or_create(
                    wp_id=post_id, wp_type='page',
                    defaults={
                        'title': title,
                        'slug': slug[:255],
                        'path': (link or slug).split('//')[-1].split('/', 1)[-1].strip('/'),
                        'excerpt_html': excerpt_html,
                        'content_html': content_html,
                        'status': status,
                        'original_url': link or '',
                        'published_at': published_at,
                        'modified_at': modified_at,
                    }
                )
            elif post_type == 'post' and do_posts and post_id:
                post, _ = Post.objects.update_or_create(
                    wp_id=post_id, wp_type='post',
                    defaults={
                        'title': title,
                        'slug': slug[:255],
                        'excerpt_html': excerpt_html,
                        'content_html': content_html,
                        'status': status,
                        'original_url': link or '',
                        'published_at': published_at,
                        'modified_at': modified_at,
                    }
                )
