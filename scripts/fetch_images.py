"""
Fetch image assets referenced in reference/lcpsych.html and rewrite body HTML
to point to local /static paths. Outputs reference/lcpsych_body_local.html.

Run: python scripts/fetch_images.py
"""
from __future__ import annotations

import os
import re
import sys
from html import unescape
from urllib.parse import urlparse
from urllib.request import urlopen, Request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REF_HTML = os.path.join(ROOT, "reference", "lcpsych.html")
OUT_BODY = os.path.join(ROOT, "reference", "lcpsych_body_local.html")
MEDIA_ROOT = os.path.join(ROOT, "static", "media", "lcpsych")
CSS_DIRS = [
    os.path.join(ROOT, "static", "css"),
    os.path.join(ROOT, "reference", "css"),
]


IMG_EXT_RE = r"(?i)\.(png|jpe?g|gif|webp|svg)"


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def find_body_inner(html: str) -> str:
    # crude but effective: find first <body ...> and closing </body>
    start = re.search(r"<body\b[^>]*>", html, flags=re.IGNORECASE)
    end = re.search(r"</body>", html, flags=re.IGNORECASE)
    if not start or not end:
        raise RuntimeError("Could not locate <body>...</body> in reference HTML")
    return html[start.end() : end.start()]


def extract_urls(html: str) -> set[str]:
    urls: set[str] = set()
    # src="..."
    for m in re.finditer(r"src=\"(https?://[^\"]+?)\"", html, flags=re.IGNORECASE):
        url = m.group(1)
        if re.search(IMG_EXT_RE, url):
            urls.add(url)
    # srcset="..." (comma-separated)
    for m in re.finditer(r"srcset=\"(.*?)\"", html, flags=re.IGNORECASE | re.DOTALL):
        val = unescape(m.group(1))
        parts = [p.strip().split(" ")[0] for p in val.split(",")]
        for p in parts:
            if p.startswith("http") and re.search(IMG_EXT_RE, p):
                urls.add(p)
    # style="background-image:url('...')"
    for m in re.finditer(r"url\((['\"]?)(https?://[^)\'\"]+?)\1\)", html, flags=re.IGNORECASE):
        url = m.group(2)
        if re.search(IMG_EXT_RE, url):
            urls.add(url)
    # og:image and twitter:image in head (we'll rewrite later in the template separately), but include for download
    for m in re.finditer(r"content=\"(https?://[^\"]+?)\"", html, flags=re.IGNORECASE):
        url = m.group(1)
        if re.search(IMG_EXT_RE, url):
            urls.add(url)
    return urls


def local_path_for(url: str) -> tuple[str, str]:
    """
    Given a remote URL, return tuple (abs_path, web_path) where
    - abs_path is the absolute file path under MEDIA_ROOT preserving the URL path
    - web_path is the web path starting with /static/... used in HTML
    """
    parsed = urlparse(url)
    remote_path = parsed.path.lstrip("/")
    # Preserve the remote path under MEDIA_ROOT to avoid name collisions
    abs_path = os.path.join(MEDIA_ROOT, remote_path)
    web_path = f"/static/media/lcpsych/{remote_path}"
    return abs_path, web_path


def download(url: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    # Skip if exists with non-zero size
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return
    try:
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
                "Referer": "https://www.lcpsych.com/",
            },
        )
        with urlopen(req) as resp, open(dest, "wb") as f:
            f.write(resp.read())
    except Exception as e:
        print(f"WARN: failed to download {url}: {e}")


def rewrite_html_to_local(html: str, url_map: dict[str, str]) -> str:
    # Replace longest URLs first to avoid substring collisions
    for url in sorted(url_map.keys(), key=len, reverse=True):
        html = html.replace(url, url_map[url])
    return html


def process_css_files(url_map: dict[str, str]) -> set[str]:
    """Scan CSS files for remote images, download them, and rewrite CSS in place.

    Returns set of all image URLs found in CSS (for download bookkeeping).
    """
    found: set[str] = set()
    css_url_re = re.compile(r"url\((['\"]?)(https?://[^)\'\"]+?)\1\)", re.IGNORECASE)
    for css_dir in CSS_DIRS:
        if not os.path.isdir(css_dir):
            continue
        for root, _dirs, files in os.walk(css_dir):
            for fn in files:
                if not fn.endswith(".css"):
                    continue
                p = os.path.join(root, fn)
                try:
                    content = read_file(p)
                except Exception:
                    continue
                urls_in_css = [m.group(2) for m in css_url_re.finditer(content)]
                urls_in_css = [u for u in urls_in_css if re.search(IMG_EXT_RE, u or "")]
                if not urls_in_css:
                    continue
                changed = False
                for url in urls_in_css:
                    found.add(url)
                    if url not in url_map:
                        abs_path, web_path = local_path_for(url)
                        download(url, abs_path)
                        url_map[url] = web_path
                    # replace in content
                    new = url_map[url]
                    if url in content:
                        content = content.replace(url, new)
                        changed = True
                if changed:
                    write_file(p, content)
    return found


def main() -> int:
    html = read_file(REF_HTML)
    body_inner = find_body_inner(html)
    urls = extract_urls(html)  # include head images too
    print(f"Found {len(urls)} image URLs in HTML (head + body)")

    url_map: dict[str, str] = {}
    for url in sorted(urls):
        abs_path, web_path = local_path_for(url)
        download(url, abs_path)
        url_map[url] = web_path

    # Also scan CSS files for remote images and rewrite CSS
    css_urls = process_css_files(url_map)
    if css_urls:
        print(f"Processed {len(css_urls)} CSS image URLs")

    # Rewrite only the body content to local paths
    body_local = rewrite_html_to_local(body_inner, url_map)
    write_file(OUT_BODY, body_local)
    print(f"Wrote body HTML with local paths to: {OUT_BODY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
