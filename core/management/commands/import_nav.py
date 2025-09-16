from django.core.management.base import BaseCommand, CommandParser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from core.models import NavItem


class Command(BaseCommand):
    help = "Import primary navigation by parsing the site header links."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--site', type=str, required=True, help='Site base URL, e.g. https://lcpsych.com')
        parser.add_argument('--truncate', action='store_true', help='Clear existing nav before import')

    def handle(self, *args, **options):
        base = options['site'].rstrip('/')
        if options['truncate']:
            NavItem.objects.all().delete()

        r = requests.get(base, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # Try to find common header nav containers
        nav = soup.find('nav') or soup.find('header') or soup
        links = []
        for a in nav.find_all('a', href=True):
            text = (a.get_text() or '').strip()
            href = a['href']
            if not text:
                continue
            url = urljoin(base+'/', href)
            # Skip anchors and mailto/tel
            if url.startswith('mailto:') or url.startswith('tel:') or '#' in href:
                continue
            links.append((text, url))

        # Deduplicate and keep order
        seen = set()
        items = []
        for title, url in links:
            if url in seen:
                continue
            seen.add(url)
            items.append((title, url))

        host = urlparse(base).netloc
        filtered = []
        for title, url in items:
            is_external = urlparse(url).netloc != host
            filtered.append((title, url, is_external))

        for idx, (title, url, is_external) in enumerate(filtered[:12]):
            NavItem.objects.get_or_create(title=title, url=url, defaults={'order': idx, 'is_external': is_external})

        self.stdout.write(self.style.SUCCESS('Navigation import complete.'))
