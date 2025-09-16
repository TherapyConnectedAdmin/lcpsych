import os
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings

from core.models import Page, Post


class Command(BaseCommand):
    help = "Download images referenced in Page/Post HTML and rewrite to local MEDIA URLs."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--site', type=str, required=True, help='Base site domain to match for media, e.g. https://www.lcpsych.com')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of documents to process (0 = all)')

    def handle(self, *args, **options):
        base = options['site'].rstrip('/')
        limit = options['limit']
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        def download_and_localize(url: str) -> str | None:
            """Download url if on allowed host; return local MEDIA url or None."""
            if not url:
                return None
            abs_url = url if url.startswith('http') else urljoin(base + '/', url)
            netloc = urlparse(abs_url).netloc
            if netloc not in (urlparse(base).netloc, 'lcpsych.com', 'www.lcpsych.com'):
                return None
            filename = os.path.basename(urlparse(abs_url).path) or 'file'
            # Strip querystrings from filename
            filename = filename.split('?')[0]
            # Ensure unique filename if collision
            target = os.path.join(settings.MEDIA_ROOT, filename)
            name, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(target):
                # Already downloaded — reuse
                break
            if not os.path.exists(target):
                try:
                    r = requests.get(abs_url, timeout=30)
                    r.raise_for_status()
                    with open(target, 'wb') as f:
                        f.write(r.content)
                except Exception as e:
                    self.stderr.write(f"Failed to download {abs_url}: {e}")
                    return None
            return settings.MEDIA_URL + os.path.basename(target)

        url_pattern = re.compile(r"url\((['\"]?)([^)\"']+)\1\)")

        def process(html: str) -> str:
            soup = BeautifulSoup(html or '', 'html.parser')
            changed = False
            # <img src>
            for img in soup.find_all('img'):
                src = img.get('src')
                local = download_and_localize(src)
                if local:
                    img['src'] = local
                    changed = True
                # srcset values
                srcset = img.get('srcset')
                if srcset:
                    parts = [p.strip() for p in srcset.split(',')]
                    new_parts = []
                    for part in parts:
                        if ' ' in part:
                            url_part, descriptor = part.split(' ', 1)
                        else:
                            url_part, descriptor = part, ''
                        local2 = download_and_localize(url_part)
                        new_parts.append(((local2 or url_part) + ((' ' + descriptor) if descriptor else '')))
                    img['srcset'] = ', '.join(new_parts)
                    changed = True
            # Inline styles with background-image
            for el in soup.find_all(style=True):
                style = el.get('style') or ''
                def repl(m):
                    quote, url_val = m.group(1), m.group(2)
                    local = download_and_localize(url_val)
                    return f"url({quote}{local or url_val}{quote})"
                new_style = url_pattern.sub(repl, style)
                if new_style != style:
                    el['style'] = new_style
                    changed = True
            # <style> blocks inside content
            for style_tag in soup.find_all('style'):
                css = style_tag.string or ''
                new_css = url_pattern.sub(lambda m: f"url({m.group(1)}{download_and_localize(m.group(2)) or m.group(2)}{m.group(1)})", css)
                if new_css != css:
                    style_tag.string = new_css
                    changed = True
            return str(soup) if changed else html

        pages = Page.objects.all()
        posts = Post.objects.all()
        count = 0
        for obj in list(pages) + list(posts):
            original = obj.content_html
            updated = process(original)
            if updated != original:
                obj.content_html = updated
                obj.save(update_fields=['content_html'])
            count += 1
            if limit and count >= limit:
                break
        self.stdout.write(self.style.SUCCESS('Media import complete.'))
