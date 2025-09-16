# LC Psych (Django + Heroku)

Starter Django project pre-configured for Heroku. Includes Whitenoise, Gunicorn, env-based settings, and a `core` app with a home page.

## Local run

```bash
# macOS/zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deploy to Heroku

1. Create app and Postgres addon.
2. Set env vars `SECRET_KEY`, `ALLOWED_HOSTS`, and Heroku provides `DATABASE_URL`.
3. Push code; Heroku will use `Procfile` and `runtime.txt`.

## WordPress import

Provide either:
- The public WordPress site URL, so we can fetch content via the WordPress REST API, or
- A WordPress export (WXR XML) and uploads archive for a fuller migration.

Run placeholder command (to be implemented):

```bash
python manage.py import_wordpress --wxr path/to/export.xml
# or
python manage.py import_wordpress --site https://example.com
```
