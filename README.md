# sudheer.su-do.in

Sudheer K's personal site — resume, work experience, projects, and side-project apps
(shareable as a standalone resume URL). Deployed via GitHub Pages, custom domain set in `CNAME`.

## Structure

- `index.html` — the site. Plain HTML, no build step or framework.
- `assets/css/main.css` / `assets/js/main.js` — the current design system (dark, terminal-inspired,
  shared visual language with [su-do.in](https://su-do.in)).
- `assets/files/` — downloadable resume PDF.
- `assets/img/` — favicon, app icons, misc images.
- `apps/librarian_assist/` — a legacy per-app landing + privacy-policy page, kept live because
  it's still linked from the Play Console listing. It intentionally still runs on the old
  `assets/css/style.css` and `assets/vendor/` (Bootstrap, Boxicons, AOS) — see below.
- `scripts/` — small local maintenance tools (see below). Not part of the deployed site's
  content, just how content gets updated.

## Updating the resume PDF

1. Edit `scripts/resume_source.txt` — put the path to your current resume PDF on the last line.
2. Run:
   ```
   python scripts/update_resume.py
   ```
   This copies it to `assets/files/Sudheer-K-Resume.pdf`, the file the "Download Resume" buttons
   link to. No other files need to change.

## Updating the Photography grid

The `#photography` section on the site (`index.html`) links each grid tile straight to an
Instagram post — clicking goes to Instagram, but the tile itself shows a locally hosted photo,
not a live embed (Instagram's embed widget can't be restyled or read from JS — it's a
cross-origin iframe — so a real image file is the only way to get a clean square tile).

1. Edit `scripts/photos_source.txt` — one Instagram post/reel URL per line, in the order you
   want them to appear. That's the only input; no file paths or slot numbers needed.
2. Run:
   ```
   pip install pillow   # once
   python scripts/update_photos.py
   ```
   For each URL, the script fetches Instagram's public embed page
   (`instagram.com/p/<id>/embed/captioned/`), pulls the real photo/cover-frame image and the
   caption, center-crops the image to a square, and saves it to
   `assets/img/photography/<n>.jpg`. It then rewrites the tile grid in `index.html` (between the
   `PHOTOS:START`/`PHOTOS:END` markers) with the correct links, captions (as `alt`/`title`), and
   reel badges — no manual HTML editing.

   This depends on the structure of Instagram's embed page, which isn't a documented/stable API
   and can change without notice. If a particular URL stops extracting cleanly, that one tile
   just falls back to the camera-icon placeholder — it won't break the rest of the run. Re-run
   the script any time; it always regenerates the full grid from `photos_source.txt`.

## Updating the Blog section

The `#blog` section pulls from your Medium RSS feed (`https://medium.com/feed/@zudheer`) — no
manual data entry needed, unlike the two tools above.

Run:
```
python scripts/update_blog.py
```
It fetches the feed, takes the latest 6 posts, and rewrites the block between the
`<!-- BLOG:START -->` / `<!-- BLOG:END -->` markers in `index.html` with fresh titles, dates,
tags, and excerpts. Don't hand-edit inside those markers — the next run overwrites them. Run this
after publishing a new Medium post. No third-party dependencies (stdlib only).

## About `assets/vendor/` and `assets/css/style.css`

The site originally started from the BootstrapMade **MyResume** template:

- Template URL: https://bootstrapmade.com/free-html-bootstrap-template-my-resume/
- Author: BootstrapMade.com
- License: https://bootstrapmade.com/license/

`index.html` no longer uses it — it was fully rebuilt on a custom stylesheet
(`assets/css/main.css`) with no Bootstrap/jQuery/AOS dependency. The original template's CSS and
`assets/vendor/` files are still present only because `apps/librarian_assist/` depends on them. Don't
delete those without first migrating or removing that page.
