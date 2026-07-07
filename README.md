# engrhassankamran.com

Single-page résumé site for **Hassan Kamran** — hand-authored HTML with inline CSS, a small vanilla-JS enhancement layer (scroll animations, all optional), and no build dependencies.

## Build & preview

```bash
python generate.py   # copies the page, assets, and résumé PDF into build/
python serve.py      # preview at http://localhost:8000
```

Deployed on Cloudflare Pages: every push to `main` rebuilds and publishes `build/`.

## Layout

- `index.html` — the page
- `resume/hassan_kamran_resume.pdf` — the résumé, served at `/hassan-kamran-resume.pdf`
- `static/` — self-hosted fonts, favicons, portrait, social card
- `assets-src/` — sources for the social card and favicon (regeneration commands inside)
- `_redirects` / `_headers` — Cloudflare Pages routing and security/caching headers

The previous multi-page portfolio (blog, gallery, services) lives in git history prior to July 2026; all of its URLs 301 to `/`.
