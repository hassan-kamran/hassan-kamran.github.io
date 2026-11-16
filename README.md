# Hassan Kamran’s personal website

A quiet, photo-led site with a résumé, research, seven selected articles, and a gallery. Hosted at **engrhassankamran.com** on Cloudflare Pages.

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
- `content/posts.json` — article title, slug, date label, category, summary, and source credit. Entries appear in editorial order; RSS is chronological.
- `content/posts/<slug>.html` — article body. Add a matching JSON entry to publish a new post.
- `content/gallery.json` — selected event photographs with titles, alternative text, and captions, in display order.
- `resume/hassan_kamran_resume.pdf` — downloadable résumé. Update the homepage when replacing it.
- `assets-src/og-card.html` — source for the 1200×630 social-sharing image.

The generator produces the blog index, article pages, gallery, RSS feed, and sitemap. The collection combines selected personal articles from commit `de65a6b` with adapted Big0 case studies and writing. Source credits distinguish company work from personal research. Adaptation dates are labelled explicitly; original personal publication dates are retained. The historical site-building article explains that it describes an earlier version. Removed archive URLs redirect to `/blog`.

`new/` and `reference /` are supplied source materials, not deployment inputs. Selected event photographs are copied from the reference into `static/gallery/`; the portrait and résumé come from `new/`. The generator never publishes those folders.

## Editorial selection — November 2026

The selection is based on firsthand detail, practical engineering decisions, personal relevance, and support for claims. Availability in Git history alone is not a reason to republish.

| Restored article | Decision and reason |
| --- | --- |
| Agricultural sprayer drone | Keep, revised. Specific hardware, simulation, mounting decisions, and staged tests. Distinguish calculated comparisons from field results; GPS autonomy remains future work. |
| FedGAN | Keep, revised. Original research and experimental detail. Explain simulated clients and limits; remove guaranteed privacy, compliance, and clinical-performance claims. |
| How I Built This Website | Keep, lightly edited. Clear personal constraints and decisions. Explicitly label the earlier Jinja2/GitHub Pages implementation. |
| Static Site Generation with Jinja2 | Exclude. Duplicates the personal account; examples contain undefined helpers, missing imports, and inconsistent configuration names. |
| MiniSearch integration | Exclude. Unescaped HTML interpolation and regex input, incomplete handlers, and disconnected advanced examples need a technical rewrite. |
| Popover hamburger menu | Exclude. Incorrect focus-trapping claims, unsupported anchor controls, broken state styling, and a manual-popover dismissal error. |
| APTEX visit | Exclude. Authentic attendance but little concrete observation beyond a brief visit. |
| Planning a Website | Exclude. Generic agency checklist and unsupported budget guidance. |
| Brand manual | Exclude. Generic marketing advice and unreferenced statistics. |
| Website SEO | Exclude. Unsupported traffic/performance claims and generic advice do not establish firsthand value. |

Big0 additions:

- **Khan:** a clear founder-led origin story with concrete monitoring, approval, and project-management decisions. Do not carry over old beta URLs or present historical specifications as current guarantees.
- **Civic platform:** data cleanup, bilingual registration, and operating constraints provide a substantive project story. Attribute it to the team; self-hosting still has operating costs.
- **Legal-document analysis:** source traceability and the review workflow are more useful than the original sales claims. The 50-bundle evaluation is reported as a project detail, not a universal accuracy guarantee.
- **Voice interfaces:** the strongest of 21 company blogs for a focused engineering essay. Keep latency/control trade-offs, progress states, and shared screen/voice state; remove unsupported benchmarks and universal architecture claims. Credit Big0 Engineering rather than inventing personal authorship.

The manufacturing-vision essay is a reasonable future candidate after editing, but less distinctive than the selected project accounts. The synthetic-data survey overlaps FedGAN. The other Big0 blogs lean on generic advice, unreferenced numbers, or short-lived industry news.

The Big0 drone and FedGAN marketing versions were not used in preference to the stronger personal accounts: they overstate autonomy, field validation, privacy, and compliance. The FedGAN revision links to the published PLOS ONE paper.

The gallery selects five actual photographs from LUMS, STMU, NUTECH, and SZABIST. Precise event dates are omitted where reference metadata and announcements disagree. Replaced screenshots and unused archive illustrations are removed from deployment assets.
