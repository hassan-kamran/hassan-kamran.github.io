# Hassan Kamran’s personal website

A quiet, photo-led site with a résumé, research, ten restored blog posts, and a gallery. Hosted at **engrhassankamran.com** on Cloudflare Pages.

## Build and preview

```sh
python3 generate.py
python3 serve.py
```

Visit http://localhost:8000. No packages, frontend framework, or JavaScript build step required. Cloudflare Pages continues to build with `generate.py` and publish `build/` on a push to `main`.

## Editing

- `index.html` — homepage content fragment, wrapped at build time.
- `404.html` — not-found content fragment.
- `templates/base.html` — shared page shell, navigation, metadata, and footer.
- `static/site.css` — responsive styles and print layout.
- `static/site.js` — optional gallery viewer. Images remain ordinary links without JavaScript.
- `content/posts.json` — article title, slug, date, category, summary, and image.
- `content/posts/<slug>.html` — article body. Add a matching JSON entry to publish a new post.
- `content/gallery.json` — images with alternative text, captions, and dates.
- `resume/hassan_kamran_resume.pdf` — downloadable résumé. Update the homepage when replacing it.
- `assets-src/og-card.html` — source for the 1200×630 social-sharing image.

The generator produces the blog index, article pages, gallery, RSS feed, and sitemap. Blog and gallery content was recovered from commit `de65a6b`; original article dates and bodies are retained. Old `.html` article URLs still work. The historical site-building posts carry a note explaining that they describe an earlier version.

`new/` and `reference /` are supplied source materials, not deployment inputs. Only the selected portrait and résumé have been copied into the site. The generator never publishes those folders.
