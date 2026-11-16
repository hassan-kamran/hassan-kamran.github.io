# engrhassankamran.com

Hassan Kamran’s **personal website**, not a services business. The homepage covers his background, current work at Khan AI, previous company Big0 (acquired August 2026), research, and education. The blog is a curated selection of seven personal and Big0 pieces; the gallery uses five event photographs from the reference.

## Build

- `python3 generate.py` produces `build/`; standard library only.
- `python3 serve.py` previews it at http://localhost:8000 with extensionless routes.
- Cloudflare Pages builds on pushes to `main`. Do not add separate hosting infrastructure.

## Sources

- `index.html` and `404.html` are body fragments, not standalone pages.
- `templates/base.html` is the shared shell, rendered with `string.Template`.
- `static/site.css` contains all styling. Fonts are self-hosted Exo 2 and DM Sans.
- `static/site.js` only enhances gallery image links with a native dialog.
- `content/posts.json` + `content/posts/<slug>.html` define articles in curated order. Retain source credits and date labels; company articles must not be attributed solely to Hassan.
- `content/gallery.json` defines the gallery; entries appear in curated JSON order.
- `resume/hassan_kamran_resume.pdf` is the résumé source of truth. Update homepage details when replacing it. Keep the home address out of HTML.
- RSS and sitemap are generated. Do not maintain separate copies at the repository root.
- `_headers` sets a same-origin CSP. Avoid external resources and inline scripts/styles.
- `_redirects` preserves retired URLs. Do not redirect `/blog`, `/blogs/*`, `/gallery`, or `/rss.xml` away from the restored content.

## Design and content

Warm light background, restrained teal accents, rectangular photography, thin rules, and clear typography. No marketing CTAs, service offers, animated counters, or decorative reveal scripts. Keep the code straightforward and all content usable without JavaScript. Preserve accessible focus, reduced-motion support, responsive layouts, and print styles.

Retain the existing favicon (the user previously chose the Big0 mark). `new/` and `reference /` are input materials, not deployable folders. Company reference changes do not belong here. `README.md` describes ordinary editing tasks.
