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

## About `assets/vendor/` and `assets/css/style.css`

The site originally started from the BootstrapMade **MyResume** template:

- Template URL: https://bootstrapmade.com/free-html-bootstrap-template-my-resume/
- Author: BootstrapMade.com
- License: https://bootstrapmade.com/license/

`index.html` no longer uses it — it was fully rebuilt on a custom stylesheet
(`assets/css/main.css`) with no Bootstrap/jQuery/AOS dependency. The original template's CSS and
`assets/vendor/` files are still present only because `apps/librarian_assist/` depends on them. Don't
delete those without first migrating or removing that page.
