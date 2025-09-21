from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import time

try:
    import requests
except Exception:
    requests = None


class Command(BaseCommand):
    help = "Saves a small file via default_storage and prints storage details and URL; optionally checks HTTP accessibility."

    def add_arguments(self, parser):
        parser.add_argument('--path', default='healthchecks/s3.txt', help='Relative path to write within storage')
        parser.add_argument('--delete', action='store_true', help='Delete the test file after check')

    def handle(self, *args, **opts):
        storage_class = default_storage.__class__.__name__
        self.stdout.write(self.style.NOTICE(f"Default storage: {storage_class}"))
        self.stdout.write(self.style.NOTICE(f"MEDIA_URL: {settings.MEDIA_URL}"))

        path = opts['path']
        # Add a timestamp to avoid CDN/browser caching confusion
        content = ContentFile(f"OK {int(time.time())}".encode('utf-8'))
        name = default_storage.save(path, content)
        self.stdout.write(self.style.SUCCESS(f"Saved: {name}"))

        try:
            url = default_storage.url(name)
            self.stdout.write(self.style.SUCCESS(f"URL: {url}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error building URL: {e}"))
            url = None

        if url and requests is not None:
            try:
                resp = requests.get(url, timeout=10)
                self.stdout.write(self.style.SUCCESS(f"HTTP GET status: {resp.status_code}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"HTTP GET failed: {e}"))
        elif url:
            self.stdout.write(self.style.WARNING("requests not installed; skipping HTTP check"))

        if opts['delete']:
            try:
                default_storage.delete(name)
                self.stdout.write(self.style.SUCCESS("Deleted test file."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to delete test file: {e}"))
