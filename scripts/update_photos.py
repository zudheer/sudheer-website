#!/usr/bin/env python3
"""
Reads scripts/photos_source.txt (one Instagram post/reel URL per line) and:

  1. Fetches each post's public embed page and pulls the real photo/cover-
     frame image and caption straight from Instagram — no login needed.
  2. Center-crops each image to a square, resizes it, and saves it to
     assets/img/photography/<n>.jpg.
  3. Regenerates the tile grid between the PHOTOS:START / PHOTOS:END
     markers in index.html — link, image, alt/title text, and the reel
     badge where relevant — so no manual HTML editing is needed.

Usage:
    python scripts/update_photos.py

Requires Pillow:
    pip install pillow

Note: this relies on the structure of Instagram's public embed page
(https://www.instagram.com/p/<shortcode>/embed/captioned/), which isn't a
documented API and can change without notice. If a URL stops extracting
cleanly, that tile falls back to the placeholder rather than breaking the
whole run.
"""

from __future__ import annotations

import html
import io
import re
import sys
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit(
        "Pillow is required but not installed.\n"
        "Install it with:  pip install pillow"
    )

SCRIPT_DIR = Path(__file__).resolve().parent
SITE_ROOT = SCRIPT_DIR.parent
SOURCE_FILE = SCRIPT_DIR / "photos_source.txt"
INDEX_FILE = SITE_ROOT / "index.html"
OUTPUT_DIR = SITE_ROOT / "assets" / "img" / "photography"
OUTPUT_SIZE = 1080  # px, square
CAPTION_LENGTH = 140

START_MARKER = "<!-- PHOTOS:START"
END_MARKER = "<!-- PHOTOS:END -->"

URL_RE = re.compile(r"instagram\.com/(p|reel)/([^/?]+)")
IMAGE_RE = re.compile(r'class="EmbeddedMediaImage"[^>]*\ssrc="([^"]+)"')
CAPTION_RE = re.compile(r'<div class="Caption">(.*?)<div class="CaptionComments"', re.DOTALL)


def read_urls(path: Path) -> list[str]:
    if not path.exists():
        sys.exit(f"Not found: {path}")
    urls = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"^_sudheer\s*", "", text.strip())
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def extract_post(post_url: str) -> dict | None:
    m = URL_RE.search(post_url)
    if not m:
        print(f"  ! not a recognizable Instagram URL: {post_url}")
        return None
    kind, shortcode = m.groups()

    embed_url = f"https://www.instagram.com/{kind}/{shortcode}/embed/captioned/"
    try:
        page = fetch(embed_url)
    except Exception as exc:  # noqa: BLE001
        print(f"  ! could not fetch {embed_url}: {exc}")
        return None

    img_match = IMAGE_RE.search(page)
    if not img_match:
        print(f"  ! could not find image on {embed_url} (page layout may have changed)")
        return None
    image_url = html.unescape(img_match.group(1))

    cap_match = CAPTION_RE.search(page)
    caption = truncate(strip_html(cap_match.group(1)), CAPTION_LENGTH) if cap_match else ""

    return {"url": post_url, "kind": kind, "image_url": image_url, "caption": caption}


def download_and_process(image_url: str, dest_path: Path) -> None:
    req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(raw)) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        w, h = img.size
        side = min(w, h)
        left, top = (w - side) // 2, (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)
        img.save(dest_path, "JPEG", quality=88, optimize=True)


def render_tile(slot: int, post: dict | None, original_url: str) -> str:
    href = post["url"] if post else original_url
    caption = html.escape(post["caption"]) if post else ""
    reel_badge = ""
    if post and post["kind"] == "reel":
        reel_badge = (
            '\n          <span class="reel-badge">'
            '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'
            "</span>"
        )
    return (
        f'        <a href="{html.escape(href)}" target="_blank" rel="noopener">\n'
        f'          <img src="assets/img/photography/{slot}.jpg" alt="{caption}" title="{caption}" '
        f'loading="lazy" onerror="this.closest(\'a\').classList.add(\'img-missing\')">'
        f"{reel_badge}\n"
        '          <div class="overlay"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" '
        'r="4"/><circle cx="17.5" cy="6.5" r="1"/></svg></div>\n'
        "        </a>"
    )


def replace_block(html_text: str, new_grid: str) -> str:
    start = html_text.find(START_MARKER)
    end = html_text.find(END_MARKER)
    if start == -1 or end == -1:
        sys.exit("Could not find PHOTOS:START / PHOTOS:END markers in index.html")
    comment_end = html_text.find("-->", start) + len("-->")
    return html_text[:comment_end] + "\n" + new_grid + "\n      " + html_text[end:]


def main() -> None:
    urls = read_urls(SOURCE_FILE)
    if not urls:
        print("No URLs in photos_source.txt — nothing to do.")
        return

    tiles = []
    ok, failed = 0, 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        post = extract_post(url)
        if post:
            try:
                download_and_process(post["image_url"], OUTPUT_DIR / f"{i}.jpg")
                print(f"  ok -> assets/img/photography/{i}.jpg  ({post['caption'][:60]!r})")
                ok += 1
            except Exception as exc:  # noqa: BLE001
                print(f"  ! download/processing failed: {exc}")
                post = None
                failed += 1
        else:
            failed += 1
        tiles.append(render_tile(i, post, url))

    html_text = INDEX_FILE.read_text(encoding="utf-8")
    grid = '      <div class="photo-grid reveal">\n' + "\n".join(tiles) + "\n      </div>"
    INDEX_FILE.write_text(replace_block(html_text, grid), encoding="utf-8")

    print(f"\nDone: {ok} updated, {failed} failed (fell back to placeholder tiles).")
    print(f"Updated {INDEX_FILE.relative_to(SITE_ROOT)}")


if __name__ == "__main__":
    main()
