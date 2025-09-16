#!/usr/bin/env python3
import re
from pathlib import Path

HOME = Path(__file__).resolve().parents[1] / 'templates' / 'home.html'

def normalize_links(text: str) -> str:
    original = text
    # 1) Anchors: https://www.lcpsych.com/#section or https://lcpsych.com#section -> #section
    text = re.sub(r'href=(\"|\")(?:https?://)?(?:www\.)?lcpsych\.com/(?:#([^\"\"]+))\1', r'href=\1#\2\1', text, flags=re.IGNORECASE)
    text = re.sub(r'href=(\"|\")(?:https?://)?(?:www\.)?lcpsych\.com#([^\"\"]+)\1', r'href=\1#\2\1', text, flags=re.IGNORECASE)

    # 2) Home root: https://www.lcpsych.com or .../ -> /
    text = re.sub(r'href=(\"|\")(?:https?://)?(?:www\.)?lcpsych\.com/?\1', r'href=\1/\1', text, flags=re.IGNORECASE)

    # 3) Same-site paths: https://www.lcpsych.com/foo/bar?x#y -> /foo/bar?x#y
    # Note: run after root/anchors so they don't match
    text = re.sub(r'href=(\"|\")(?:https?://)?(?:www\.)?lcpsych\.com(/[^\"\"]*)\1', r'href=\1\2\1', text, flags=re.IGNORECASE)

    # 4) Remove target/rel from same-site links (href starting with / or #)
    def remove_target_rel(m: re.Match) -> str:
        tag = m.group(0)
        # Drop target and rel attributes
        tag = re.sub(r'\s+target=\"[^\"]*\"', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+rel=\"[^\"]*\"', '', tag, flags=re.IGNORECASE)
        return tag

    text = re.sub(r'<a\b([^>]*?)href=\"[\/#][^\"]*\"([^>]*)>', remove_target_rel, text, flags=re.IGNORECASE)

    return text


def main():
    if not HOME.exists():
        raise SystemExit(f"File not found: {HOME}")
    src = HOME.read_text(encoding='utf-8')
    out = normalize_links(src)
    if out != src:
        HOME.write_text(out, encoding='utf-8')
        print('Updated home.html hyperlinks to local paths.')
    else:
        print('No changes needed.')

if __name__ == '__main__':
    main()
