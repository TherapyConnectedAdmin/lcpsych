#!/usr/bin/env python3
"""
Localize external assets referenced in templates/base.html.

- Downloads lcpsych.com CSS files to static/vendor/lcpsych/<remote_path>
- Rewrites CSS url(...) references to local copies and downloads images/fonts
- Rewrites <link rel="stylesheet"> hrefs in templates/base.html to /static paths
- Rewrites favicon/apple-touch icon hrefs in head to /static paths
- Removes/remaps third-party trackers (GTM/Adsense) script/link tags

Run: python scripts/localize_assets.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import os as _os

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "base.html"
VENDOR_ROOT = ROOT / "static" / "vendor" / "lcpsych"
FONTS_ROOT = ROOT / "static" / "fonts"
LOCAL_FONTS_CSS = ROOT / "static" / "css" / "local-fonts.css"

HEAD_IMG_EXT = re.compile(r"(?i)\.(png|jpe?g|gif|webp|svg|ico)")
CSS_URL_RE = re.compile(r"url\((['\"]?)(https?:|//)([^)\'\"]+?)\1\)")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, data: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    # Normalize protocol-relative
    if url.startswith("//"):
        url = "https:" + url
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        "Referer": "https://www.lcpsych.com/",
    })
    try:
        with urlopen(req) as resp, open(dest, "wb") as f:
            f.write(resp.read())
    except Exception as e:
        print(f"WARN: failed to download {url}: {e}")


def local_path_for(url: str) -> tuple[Path, str]:
    if url.startswith("//"):
        url = "https:" + url
    parsed = urlparse(url)
    # Strip query
    remote = parsed.path.lstrip("/")
    abs_path = VENDOR_ROOT / remote
    web_path = "/static/vendor/lcpsych/" + remote
    return abs_path, web_path


def rewrite_css_file(css_path: Path) -> None:
    try:
        css = read(css_path)
    except Exception:
        return
    changed = False
    for m in list(CSS_URL_RE.finditer(css)):
        full = m.group(0)
        proto = m.group(2)
        rest = m.group(3)
        remote_url = ("https:" if proto == "//" else "") + proto + rest if proto == "//" else proto + rest  # fallback
        # Fix construction
        if remote_url.startswith("https:https"):
            remote_url = "https://" + rest
        if not remote_url.startswith("http"):
            continue
        dest, web = local_path_for(remote_url)
        download(remote_url, dest)
        if dest.exists() and dest.stat().st_size > 0:
            css = css.replace(full, f"url('{web}')")
            changed = True
    if changed:
        write(css_path, css)


def remove_trackers(html: str) -> str:
    """Legacy destructive removal of trackers (kept for non-preserve mode)."""
    html = re.sub(r"<script[^>]*>[\s\S]*?(googletagmanager|googlesyndication|adsbygoogle)[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<script[^>]*(googletagmanager|googlesyndication|adsbygoogle)[^>]*>[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<link[^>]+dns-prefetch[^>]+(googletagmanager|googlesyndication)[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<meta[^>]+name=([\"'])generator\1[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<meta[^>]+name=([\"'])google-adsense-platform-[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<script[^>]*>[\s\S]*?(gtag\(|dataLayer\s*=)[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
    return html


def rewrite_trackers_to_local(html: str) -> str:
    """Preserve tracker tags but swap external URLs to local stub JS to avoid network calls."""
    replacements = {
        # GTAG bootstrap loader
        r"https://www\.googletagmanager\.com/gtag/js\?id=[^'\"]+": "/static/js/stubs/gtag.js",
        # GTM
        r"https://www\.googletagmanager\.com/gtm\.js[^'\"]*": "/static/js/stubs/gtm.js",
        # Adsense
        r"https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^'\"]*": "/static/js/stubs/adsbygoogle.js",
    }
    for pat, local in replacements.items():
        html = re.sub(pat, local, html)
    # Normalize GTM loader assignment that may still concatenate id/dl
    html = re.sub(r"j\.src\s*=\s*['\"]/static/js/stubs/gtm\.js['\"][^;]*;", "j.src='/static/js/stubs/gtm.js';", html)
    return html


def fetch_google_fonts_locally() -> None:
    """Fetch selected Google Fonts families and produce a local CSS with self-hosted files.

    - Requests CSS from fonts.googleapis with a modern UA to prefer WOFF2.
    - Downloads any referenced font files (woff2/woff/ttf) to /static/fonts/<family>/.
    - Rewrites all fonts.gstatic.com URLs in the CSS to their /static paths.
    """
    families = {
        # family: (ital, weights)
        "Poppins": {
            "normal": [300, 400, 500, 600, 700],
            "italic": [400, 600],
        },
        "Montserrat": {
            "normal": [300, 400, 500, 600, 700],
            "italic": [400, 600],
        },
        "Figtree": {
            "normal": [400, 600, 700],
        },
    }

    def family_query(fam: str, styles: dict) -> str:
        parts = []
        if "italic" in styles:
            pairs = [f"0,{w}" for w in styles.get("normal", [])] + [f"1,{w}" for w in styles["italic"]]
            parts.append(f"family={fam}:ital,wght@" + ";".join(pairs))
        else:
            parts.append(f"family={fam}:wght@" + ";".join(str(w) for w in styles.get("normal", [])))
        return "&".join(parts)

    css_blocks: list[str] = []
    for fam, styles in families.items():
        q = family_query(fam, styles)
        url = f"https://fonts.googleapis.com/css2?{q}&display=swap"
        # Use a modern desktop UA to get woff2 sources
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
            "Accept": "text/css,*/*;q=0.1",
        })
        try:
            with urlopen(req) as resp:
                css = resp.read().decode("utf-8")
        except Exception as e:
            print(f"WARN: failed to fetch CSS for {fam}: {e}")
            continue
        # Collect all font file URLs (prefer woff2 but include fallbacks)
        urls = re.findall(r"https://fonts\.gstatic\.com/[^)\"']+\.(?:woff2|woff|ttf)", css)
        local_css = css
        for fu in urls:
            parsed = urlparse(fu)
            dest = FONTS_ROOT / fam.lower() / os.path.basename(parsed.path)
            download(fu, dest)
            web = f"/static/fonts/{fam.lower()}/{os.path.basename(parsed.path)}"
            local_css = local_css.replace(fu, web)
        # As an extra guard, replace any remaining fonts.gstatic.com URLs with placeholders under /static/fonts
        local_css = re.sub(
            r"https://fonts\.gstatic\.com/[^)\"']+/(?:[^/]+)$",
            lambda m: f"/static/fonts/{fam.lower()}/" + os.path.basename(urlparse(m.group(0)).path),
            local_css,
        )
        css_blocks.append(local_css)

    if css_blocks:
        LOCAL_FONTS_CSS.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_FONTS_CSS.write_text("\n\n".join(css_blocks), encoding="utf-8")


def ensure_fonts_link(html: str) -> str:
    """Ensure <link rel=stylesheet href="/static/css/local-fonts.css"> is present once near other styles."""
    if "/static/css/local-fonts.css" in html:
        return html
    link_tag = '<link rel="stylesheet" href="/static/css/local-fonts.css" media="all"/>'
    # Insert before icons block or before closing head
    insert_before = html.rfind("<link rel=\"icon\"")
    if insert_before == -1:
        insert_before = html.lower().rfind("</head>")
    if insert_before != -1:
        return html[:insert_before] + link_tag + "\n    " + html[insert_before:]
    return link_tag + html


def main() -> int:
    html = read(TEMPLATE)

    # Collect <link rel=stylesheet> and icon hrefs
    href_re = re.compile(r"<link[^>]+(rel=\"stylesheet\"|rel='stylesheet')[^>]+href=([\"'])(?P<href>https?:[^\"']+|//[^\"']+)[\"'][^>]*>", re.IGNORECASE)
    icon_re = re.compile(r"<link[^>]+(rel=\"(?:icon|apple-touch-icon)\"|rel='(?:icon|apple-touch-icon)')[^>]+href=([\"'])(?P<href>https?:[^\"']+|//[^\"']+)[\"'][^>]*>", re.IGNORECASE)
    ms_tile_re = re.compile(r"<meta[^>]+name=([\"'])msapplication-TileImage\1[^>]+content=([\"'])(?P<href>https?:[^\"']+|//[^\"']+)[\"'][^>]*>", re.IGNORECASE)
    meta_img_re = re.compile(r"<meta[^>]+(property=([\"'])og:image\2|name=([\"'])twitter:image\3)[^>]+content=([\"'])(?P<href>https?:[^\"']+|//[^\"']+)[\"'][^>]*>", re.IGNORECASE)
    css_urls = [m.group('href') for m in href_re.finditer(html)]
    icon_urls = [m.group('href') for m in icon_re.finditer(html)]
    tile_urls = [m.group('href') for m in ms_tile_re.finditer(html)]
    meta_img_urls = [m.group('href') for m in meta_img_re.finditer(html)]

    # Download CSS files from lcpsych.com only; rewrite to /static paths
    url_map: dict[str, str] = {}
    for url in css_urls:
        target_hosts = ("lcpsych.com", "www.lcpsych.com")
        host = urlparse("https:" + url if url.startswith("//") else url).netloc
        if not any(h in host for h in target_hosts):
            continue
        dest, web = local_path_for(url)
        download(url, dest)
        url_map[url] = web
        # Also rewrite CSS url(...) inside the downloaded file and fetch those assets
        rewrite_css_file(dest)

    # Download icons
    for url in icon_urls:
        dest, web = local_path_for(url)
        if not HEAD_IMG_EXT.search(dest.suffix):
            # allow svg/png/webp/ico
            pass
        download(url, dest)
        url_map[url] = web

    # Download msapplication tile image
    for url in tile_urls:
        dest, web = local_path_for(url)
        download(url, dest)
        url_map[url] = web

    # Download and rewrite social images
    for url in meta_img_urls:
        dest, web = local_path_for(url)
        download(url, dest)
        url_map[url] = web

    # Replace references in HTML (longest first)
    for url in sorted(url_map.keys(), key=len, reverse=True):
        html = html.replace(url, url_map[url])
        # also protocol-relative variants
        if url.startswith("http"):
            proto_rel = url.replace("https:", "").replace("http:", "")
            html = html.replace(proto_rel, url_map[url])

    # Either remove trackers (legacy) or preserve and rewrite to local stubs
    preserve = _os.environ.get("PRESERVE_HEAD", "1") == "1"
    if preserve:
        html = rewrite_trackers_to_local(html)
        # Also ensure local fonts link is present (optional)
        fetch_google_fonts_locally()
        html = ensure_fonts_link(html)
    else:
        html = remove_trackers(html)

    write(TEMPLATE, html)
    print(f"Localized {len(url_map)} assets and updated base.html (preserve_head={preserve})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
