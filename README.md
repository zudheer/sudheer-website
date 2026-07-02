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
not an embed (Instagram's embed widget can't be restyled or read from JS — it's a cross-origin
iframe — so a real image file is the only way to get a clean square tile).

1. Edit `scripts/photos_source.txt` — for each numbered slot (matches the tile's position on the
   page), paste the path to a photo on your computer. The Instagram permalink shown next to each
   number is just a reminder of which post that slot links to.
2. Run:
   ```
   pip install pillow   # once
   python scripts/update_photos.py
   ```
   Each photo gets center-cropped to a square, resized, and saved to
   `assets/img/photography/<slot>.jpg`. `index.html` already points at those exact filenames, so
   no HTML changes are needed — refresh the page and the new photos show up. Any slot without a
   file yet falls back to a camera-icon placeholder instead of a broken image.

## About `assets/vendor/` and `assets/css/style.css`

The site originally started from the BootstrapMade **MyResume** template:

- Template URL: https://bootstrapmade.com/free-html-bootstrap-template-my-resume/
- Author: BootstrapMade.com
- License: https://bootstrapmade.com/license/

`index.html` no longer uses it — it was fully rebuilt on a custom stylesheet
(`assets/css/main.css`) with no Bootstrap/jQuery/AOS dependency. The original template's CSS and
`assets/vendor/` files are still present only because `apps/librarian_assist/` depends on them. Don't
delete those without first migrating or removing that page.
