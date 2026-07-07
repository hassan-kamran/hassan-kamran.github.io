# CLAUDE.md — engrhassankamran.com

## About This Site

A **single-page résumé site** for Hassan Kamran, served at https://engrhassankamran.com on Cloudflare Pages.

Until July 2026 this repo held a multi-page portfolio (blog, gallery, services, separate resume page) built with a Jinja2 static generator. That was all retired in favour of one hand-authored page (old code is in git history). Every old URL 301-redirects to `/` via `_redirects`.

## Structure

```
index.html          # THE page — hand-authored HTML with inline CSS
static/site.js      # progressive enhancement: reveals, counters, scroll-spy, spotlight, copy buttons
404.html            # minimal not-found page
resume/hassan_kamran_resume.pdf   # source of truth for content; served at /hassan-kamran-resume.pdf
static/             # fonts (woff2), HK favicons, portrait photo, og-card.jpg, site.webmanifest
assets-src/         # og-card.html and favicon.html sources (regeneration cmds in their comments)
generate.py         # stdlib-only build: copies everything into build/ (exit 1 on missing files)
serve.py            # local preview of build/ with Cloudflare-style extensionless URLs
_redirects _headers robots.txt sitemap.xml   # Cloudflare Pages config, copied into build/
```

## Key Commands

```bash
python generate.py   # build into build/ (no dependencies needed; uv run also works)
python serve.py      # preview at http://localhost:8000
```

Deployment: push to `main` → Cloudflare Pages builds `generate.py` → serves `build/`.

## Updating Content

- **Résumé changes:** the PDF in `resume/` is the source of truth. Replace the PDF *and* mirror the change in `index.html` — sections: hero summary, stats strip, Work Experience, Publications, Licences/Certifications/Courses, Education, contact details.
- **Contact info:** contact@engrhassankamran.com, +92 303 9441945, linkedin.com/in/engr-hassan-kamran, github.com/hassan-kamran, ORCID 0009-0005-3034-1679. The home address stays out of the HTML (it's only inside the PDF).
- **OG image:** edit `assets-src/og-card.html`, then regenerate `static/og-card.jpg` with the headless-Chrome + sips commands in that file's top comment.
- **Favicons:** the Big0 "0" mark on teal, copied verbatim from the company repo (`Big0-dev.github.io/static/favicon*`) — Hassan's explicit choice for his personal site too. To update, replace the files in `static/` (ico, svg, png sizes, apple-touch-icon) rather than redesigning.
- **New pages:** don't add any without being asked — the whole point is one page. If one is truly needed, add the filename to `PAGES` in `generate.py`.
- **Animations are progressive enhancement** in `static/site.js` (script tag carries `?v=N` — bump it on every site.js change; _headers rules must use EXACT paths, mid-pattern splats never match) (reveal-on-scroll, stat count-up, kicker decode, career-stepper activation, timeline draw, scroll-spy, hero spotlight, copy-to-clipboard, back-to-top). Rules: every hidden/dim initial state must be scoped under `html.js` inside `@media screen and (prefers-reduced-motion: no-preference)` so the page stays fully readable with JS off, motion off, and in print; `html:not(.js)` fallbacks light the stepper/timeline dots statically.
- **CSP** in `_headers` is `default-src 'none'` + `script-src 'self'` — adding any external resource requires loosening it deliberately. There's also a print stylesheet at the bottom of `index.html` (flips the design tokens to light ink) — keep it in mind when adding sections.

## Related

- **big0.dev** (`/Users/hassan/Code/Big0-dev.github.io`) is the SEPARATE company site for Big0 Dev (Pvt) Ltd — a full multi-page marketing site. Résumé/personal changes belong HERE, not there.

## Design System

- **Dark theme only** — no light mode, no gradients
- Colors: void `#0A0F1C` (bg), panel `#0F172A`, borders `#1E293B`/`#334155`, signal teal `#0D9488`, glow `#14B8A6`, bright `#2DD4BF`, text `#CBD5E1`, muted `#94A3B8`
- Fonts (self-hosted woff2): "Exo 2" (display/headings), "DM Sans" (body)
- Radius 10–12px, transitions 0.2s ease, content max-width 1000px, mobile breakpoint 768px
- All CSS is inline in `index.html` — no external stylesheet, so no cache-busting needed. Fonts are cached immutable via `_headers`.

## Gotchas

- `find` is aliased to `fd` in this shell — use `/usr/bin/find`
- zsh does not word-split unquoted variables — don't write `for f in $LIST` in Bash tool calls
- headless Chrome has a ~500px minimum window width; fragment URLs (`#section`) don't scroll before `--screenshot` fires — capture full pages with a tall `--window-size` instead
- The résumé PDF must be committed (Cloudflare builds from git); `generate.py` fails the build if it's missing
