#!/usr/bin/env python3
"""
Fetches https://medium.com/feed/@zudheer and regenerates the Blog section
in index.html (the block between the BLOG:START / BLOG:END comments) with
the latest posts.

Usage:
    python scripts/update_blog.py

No third-party dependencies — stdlib only.
"""

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SITE_ROOT = SCRIPT_DIR.parent
INDEX_FILE = SITE_ROOT / "index.html"
FEED_URL = "https://medium.com/feed/@zudheer"
POST_LIMIT = 6
EXCERPT_LENGTH = 160
TAGS_PER_POST = 3

START_MARKER = "<!-- BLOG:START"
END_MARKER = "<!-- BLOG:END -->"

MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def fetch_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def strip_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt_of(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    cut = text[:length].rsplit(" ", 1)[0]
    return cut.rstrip(",.;:") + "…"


def format_date(pub_date: str) -> str:
    # RFC 822, e.g. "Thu, 02 Jul 2026 23:48:41 GMT"
    m = re.match(r"\w+, (\d{2}) (\w+) (\d{4})", pub_date)
    if not m:
        return pub_date
    _, mon, year = m.groups()
    return f"{mon} {year}"


def clean_link(link: str) -> str:
    return link.split("?", 1)[0]


def parse_items(xml_bytes: bytes) -> list[dict]:
    ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall(".//item")[:POST_LIMIT]:
        title = (item.findtext("title") or "").strip()
        link = clean_link((item.findtext("link") or "").strip())
        pub_date = format_date((item.findtext("pubDate") or "").strip())
        categories = [c.text.strip() for c in item.findall("category") if c.text][:TAGS_PER_POST]
        content_encoded = item.findtext("content:encoded", namespaces=ns) or ""
        excerpt = excerpt_of(strip_html(content_encoded), EXCERPT_LENGTH)
        items.append(
            {
                "title": title,
                "link": link,
                "date": pub_date,
                "tags": categories,
                "excerpt": excerpt,
            }
        )
    return items


def render_card(post: dict) -> str:
    tags_html = "".join(f"<span>{html.escape(t)}</span>" for t in post["tags"])
    return (
        f'        <a class="blog-card" href="{html.escape(post["link"])}" target="_blank" rel="noopener">\n'
        f'          <span class="date">{html.escape(post["date"])}</span>\n'
        f'          <h3>{html.escape(post["title"])}</h3>\n'
        f'          <p>{html.escape(post["excerpt"])}</p>\n'
        f'          <div class="tags">{tags_html}</div>\n'
        f'          <span class="read">Read on Medium &#8599;</span>\n'
        f"        </a>"
    )


def render_grid(posts: list[dict]) -> str:
    cards = "\n".join(render_card(p) for p in posts)
    return f'      <div class="blog-grid reveal">\n{cards}\n      </div>'


def replace_block(html_text: str, new_grid: str) -> str:
    start = html_text.find(START_MARKER)
    end = html_text.find(END_MARKER)
    if start == -1 or end == -1:
        sys.exit("Could not find BLOG:START / BLOG:END markers in index.html")

    comment_end = html_text.find("-->", start) + len("-->")
    return html_text[:comment_end] + "\n" + new_grid + "\n      " + html_text[end:]


def main() -> None:
    print(f"Fetching {FEED_URL}")
    try:
        xml_bytes = fetch_feed(FEED_URL)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Could not fetch feed: {exc}")

    posts = parse_items(xml_bytes)
    if not posts:
        sys.exit("No posts found in feed — aborting without touching index.html.")

    print(f"Found {len(posts)} post(s):")
    for p in posts:
        print(f"  - [{p['date']}] {p['title']}")

    html_text = INDEX_FILE.read_text(encoding="utf-8")
    updated = replace_block(html_text, render_grid(posts))
    INDEX_FILE.write_text(updated, encoding="utf-8")

    print(f"\nUpdated {INDEX_FILE.relative_to(SITE_ROOT)}")


if __name__ == "__main__":
    main()
