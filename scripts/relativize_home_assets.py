#!/usr/bin/env python3
"""
Rewrite remaining lcpsych.com asset references in templates/home.html to local paths.

Changes applied:
- Images: https://www.lcpsych.com/wp-content/uploads/... -> /static/media/<basename>
  (applies in src, srcset, inline style url(), data-* attributes, and CSS blocks)
- Remove <script> blocks that lazy-load wp-includes hooks/i18n from lcpsych.com
- Remove protocol-relative WP Rocket/WP Fastest Cache bundle scripts to lcpsych.com
- Gravity Forms/Elementor config URLs rewritten to local vendor assets under /static/vendor/lcpsych

Run: python3 scripts/relativize_home_assets.py
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "templates" / "home.html"


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_text(p: Path, data: str) -> None:
    p.write_text(data, encoding="utf-8")


def map_upload_url_to_local(url: str) -> str:
    """Map any lcpsych uploads URL to local /static/media/<basename> path."""
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if not name:
        return url
    return f"/static/media/{name}"


def replace_uploads(doc: str) -> str:
    # Find all absolute uploads URLs in any context
    uploads_re = re.compile(r"https?://(?:www\.)?lcpsych\.com/wp-content/uploads/[^\"'\)\s]+", re.IGNORECASE)
    urls = sorted(set(m.group(0) for m in uploads_re.finditer(doc)), key=len, reverse=True)
    for url in urls:
        doc = doc.replace(url, map_upload_url_to_local(url))
    return doc


def strip_wp_includes_lazyload_scripts(doc: str) -> str:
    # Remove inline scripts that lazy-load wp-includes hooks/i18n from lcpsych.com
    pattern = re.compile(
        r"<script[^>]*data-wpfc-render=[^>]*>.*?wp-includes/js/dist/.*?</script>\s*",
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub("", doc)


def strip_wp_cache_bundle_scripts(doc: str) -> str:
    # Remove protocol-relative external cache bundle scripts
    pattern = re.compile(
        r"<script[^>]+src=\"//www\.lcpsych\.com/wp-content/cache/wpfc-minified/[^\"]+\"[^>]*></script>\s*",
        re.IGNORECASE,
    )
    return pattern.sub("", doc)


def rewrite_plugin_assets(doc: str) -> str:
    # Gravity Forms base and images
    replacements = {
        # Unescaped
        "https://www.lcpsych.com/wp-content/plugins/gravityforms": 
            "/static/vendor/lcpsych/wp-content/plugins/gravityforms",
        # Escaped
        "https:\/\/www.lcpsych.com\/wp-content\/plugins\/gravityforms": 
            "\/static\/vendor\/lcpsych\/wp-content\/plugins\/gravityforms",

        # Elementor assets
        "https://www.lcpsych.com/wp-content/plugins/elementor/assets/": 
            "/static/vendor/lcpsych/wp-content/plugins/elementor/assets/",
        "https:\/\/www.lcpsych.com\/wp-content\/plugins\/elementor\/assets\/": 
            "\/static\/vendor\/lcpsych\/wp-content\/plugins\/elementor\/assets\/",

        # Elementor Pro assets
        "https://www.lcpsych.com/wp-content/plugins/elementor-pro/assets/": 
            "/static/vendor/lcpsych/wp-content/plugins/elementor-pro/assets/",
        "https:\/\/www.lcpsych.com\/wp-content\/plugins\/elementor-pro\/assets\/": 
            "\/static\/vendor\/lcpsych\/wp-content\/plugins\/elementor-pro\/assets\/",

        # Happy Addons pdfjs
        "https://www.lcpsych.com/wp-content/plugins/happy-elementor-addons/assets/vendor/pdfjs/lib": 
            "/static/vendor/lcpsych/wp-content/plugins/happy-elementor-addons/assets/vendor/pdfjs/lib",
        "https:\/\/www.lcpsych.com\/wp-content\/plugins\/happy-elementor-addons\/assets\/vendor\/pdfjs\/lib": 
            "\/static\/vendor\/lcpsych\/wp-content\/plugins\/happy-elementor-addons\/assets\/vendor\/pdfjs\/lib",
    }
    for old, new in replacements.items():
        doc = doc.replace(old, new)
    return doc


def main() -> int:
    doc = read_text(HOME)
    before = doc

    # 1) Rewrite uploads to local media
    doc = replace_uploads(doc)

    # 2) Strip external lazyload and cache bundle scripts
    doc = strip_wp_includes_lazyload_scripts(doc)
    doc = strip_wp_cache_bundle_scripts(doc)

    # 3) Rewrite plugin config asset URLs
    doc = rewrite_plugin_assets(doc)

    if doc != before:
        write_text(HOME, doc)
        print("Rewrote templates/home.html with local asset paths and removed external scripts.")
    else:
        print("No changes made; templates/home.html already localized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
