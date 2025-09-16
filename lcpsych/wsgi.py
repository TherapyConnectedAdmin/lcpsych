"""
WSGI config for lcpsych project.

It exposes the WSGI callable as a module-level variable named ``application``.

WhiteNoise is used to serve compiled static files and (read-only) media files in
production on platforms without persistent disks (e.g., Heroku). Media here is
treated as build-time assets imported from WordPress, not user uploads.

For more information see:
 - https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
 - https://whitenoise.evans.io/en/stable/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lcpsych.settings')

application = get_wsgi_application()

# Serve static files and packaged media via WhiteNoise
BASE_DIR = Path(__file__).resolve().parent.parent
application = WhiteNoise(application)
# Expose the media directory under the /media/ URL prefix (read-only)
application.add_files(str(BASE_DIR / 'media'), prefix='media/')
