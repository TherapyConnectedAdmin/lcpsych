import re
import os
import sys
from urllib.parse import urlparse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(__file__))
REF = os.path.join(ROOT, 'reference', 'lcpsych.html')
OUT_BASE = os.path.join(ROOT, 'static', 'img', 'lcpsych')

def main():
    if not os.path.exists(REF):
        print(f"Missing reference file: {REF}", file=sys.stderr)
        sys.exit(1)
    with open(REF, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    # Find image and icon URLs
    pattern = re.compile(r'https://www\.lcpsych\.com[^\s"\')>]+\.(?:png|jpe?g|webp|svg|gif)', re.IGNORECASE)
    urls = sorted(set(pattern.findall(html)))
    print(f"Found {len(urls)} unique image URLs")
    count_ok = 0
    for url in urls:
        rel = url.split('https://www.lcpsych.com/', 1)[1]
        out_path = os.path.join(OUT_BASE, rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        try:
            urllib.request.urlretrieve(url, out_path)
            count_ok += 1
            print(f"OK {url} -> {out_path}")
        except Exception as e:
            print(f"ERR {url}: {e}")
    print(f"Downloaded {count_ok}/{len(urls)} files into {OUT_BASE}")

if __name__ == '__main__':
    main()
