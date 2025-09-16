#!/usr/bin/env python3
"""
Sanitize reference/lcpsych_body_local.html and inline into templates/home.html.

Removals:
- <noscript> GTM iframe
- Cloudflare beacon script
- Google Ads <ins> and ad iframes
- reCAPTCHA iframe
- Any script tags that lazy-load wp-includes hooks/i18n from lcpsych.com
- Duplicate jQuery .open-off-canvas handlers (keep one)

Rewrites:
- Absolute anchors like https://www.lcpsych.com/#anchor -> #anchor
- Absolute home links https://www.lcpsych.com/ -> /

Other:
- Drop leading duplicate skip-link if present (home.html already has one)
- Ensure no external <script> src to lcpsych.com/wp-includes remains
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ref_path = ROOT / "reference" / "lcpsych_body_local.html"
home_path = ROOT / "templates" / "home.html"

START_MARKER = "<!-- Reference body (inlined) START -->"
END_MARKER = "<!-- Reference body (inlined) END -->"

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def write(p: Path, data: str) -> None:
    p.write_text(data, encoding="utf-8")

def sanitize_body(html: str) -> str:
    original_len = len(html)

    # Remove GTM noscript block
    html = re.sub(r"<noscript>.*?</noscript>\s*", "", html, flags=re.DOTALL|re.IGNORECASE)

    # Remove Cloudflare beacon
    html = re.sub(r"<script[^>]+static\.cloudflareinsights\.com[^>]*></script>\s*", "", html, flags=re.IGNORECASE)

    # Remove Google Ads containers and iframes
    html = re.sub(r"<ins[^>]*adsbygoogle[^>]*>.*?</ins>\s*", "", html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r"<iframe[^>]+googleads\.g\.doubleclick\.net[^>]*></iframe>\s*", "", html, flags=re.IGNORECASE)

    # Remove reCAPTCHA iframe
    html = re.sub(r"<iframe[^>]+recaptcha[^>]*></iframe>\s*", "", html, flags=re.IGNORECASE)

    # Remove scripts that lazy-load WP hooks/i18n via lcpsych.com/wp-includes
    html = re.sub(r"<script[^>]*data-wpfc-render=[^>]*>.*?wp-includes/js/dist/.*?</script>\s*", "", html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r"<script[^>]+src=\"https?://www\.lcpsych\.com/wp-includes/js/dist/[^\"]+\"[^>]*></script>\s*", "", html, flags=re.IGNORECASE)

    # Remove duplicate .open-off-canvas jQuery handlers, keep only first occurrence block
    # Identify blocks by marker of function jqIsReady_ and handler body content
    offcanvas_blocks = re.findall(r"<script>\(function jqIsReady_[\s\S]*?</script>", html, flags=re.IGNORECASE)
    if offcanvas_blocks:
        # Keep first, remove the rest
        first = offcanvas_blocks[0]
        html = re.sub(r"<script>\(function jqIsReady_[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        # Re-append a single instance at the end of body content before closing
        html = html.rstrip()
        # Insert before last closing tag if present
        insert_pos = html.rfind("</")
        if insert_pos != -1:
            html = html[:insert_pos] + first + "\n" + html[insert_pos:]
        else:
            html += "\n" + first

    # Convert absolute site anchors to local anchors
    html = re.sub(r"href=\"https?://www\.lcpsych\.com/#([A-Za-z0-9_-]+)\"", r'href="#\1"', html)

    # Convert absolute home links to root path
    html = re.sub(r"href=\"https?://www\.lcpsych\.com/\"", 'href="/"', html)

    # Drop duplicate skip-link if present at start of captured body
    html = re.sub(r"^\s*<a[^>]*class=\"[^\"]*skip-link[^\"]*\"[\s\S]*?</a>\s*", "", html, flags=re.IGNORECASE)

    # Safety: strip any remaining external tracker scripts
    html = re.sub(r"<script[^>]+(googletagmanager|googlesyndication|adsbygoogle)[^>]*>.*?</script>", "", html, flags=re.DOTALL|re.IGNORECASE)

    # Replace any protocol-relative lcpsych.com cache bundle script/link srcs with static local equivalents if present in template already
    # Not strictly needed here; home.html already includes local JS bundles.

    print(f"Sanitized body: {original_len} -> {len(html)} chars")
    return html

def replace_between_markers(doc: str, replacement: str) -> str:
    if START_MARKER not in doc or END_MARKER not in doc:
        raise RuntimeError("Markers not found in templates/home.html")
    start = doc.index(START_MARKER) + len(START_MARKER)
    end = doc.index(END_MARKER)
    return doc[:start] + "\n" + replacement + "\n" + doc[end:]

def main():
    body_html = read(ref_path)
    sanitized = sanitize_body(body_html)
    home = read(home_path)
    updated = replace_between_markers(home, sanitized)
    write(home_path, updated)
    print("Inlined sanitized body into templates/home.html")

if __name__ == "__main__":
    main()
