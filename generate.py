#!/usr/bin/env python3
"""Build Hassan Kamran's personal site using only the Python standard library."""

import json
import shutil
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from string import Template
from xml.etree.ElementTree import Element, SubElement, ElementTree

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
SITE = "https://engrhassankamran.com"
BASE = Template((ROOT / "templates/base.html").read_text())


def read_json(name):
    return json.loads((ROOT / "content" / name).read_text())


def write_page(path, title, description, content, section="", article=False):
    output = BUILD / ("index.html" if path == "/" else path.lstrip("/") + ".html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(BASE.substitute(
        title=escape(title), description=escape(description), path=escape(path),
        content=content, year=date.today().year,
        og_type="article" if article else "website",
        blog_current='aria-current="page"' if section == "blog" else "",
        gallery_current='aria-current="page"' if section == "gallery" else "",
    ))


def post_meta(post):
    published = date.fromisoformat(post["date"])
    return (f'<div class="post-meta"><span>{escape(post["category"])}</span>'
            f'<time datetime="{post["date"]}">{published:%d %b %Y}</time></div>')


def post_row(post, preview=False):
    image = "" if preview else (f'<img src="{escape(post["image"])}" alt="" '
                                'width="170" height="128" loading="lazy">')
    heading = "h3" if preview else "h2"
    description = "" if preview else f'<p>{escape(post["description"])}</p>'
    return (f'<a class="post-row" href="/blogs/{post["slug"]}">{image}<div>'
            f'{post_meta(post)}<{heading}>{escape(post["title"])}</{heading}>'
            f'{description}</div><span class="post-arrow" aria-hidden="true">↗</span></a>')


def gallery_figure(item, preview=False):
    href = "/gallery" if preview else escape(item["src"])
    css = "" if preview else ' class="gallery-link"'
    caption = escape(item["alt"])
    if not preview:
        caption += f'<span>{escape(item["caption"])}</span>'
    return (f'<figure><a href="{href}"{css}><img src="{escape(item["src"])}" '
            f'alt="{escape(item["alt"])}" width="800" height="600" loading="lazy">'
            f'</a><figcaption>{caption}</figcaption></figure>')


def write_feeds(posts):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    for tag, value in [("title", "Hassan Kamran’s blog"), ("link", SITE + "/blog"),
                       ("description", "Notes on engineering, software, and things I’ve learned."),
                       ("language", "en")]:
        SubElement(channel, tag).text = value
    for post in posts:
        item = SubElement(channel, "item")
        for tag, value in [("title", post["title"]), ("link", SITE + "/blogs/" + post["slug"]),
                           ("description", post["description"]), ("category", post["category"]),
                           ("pubDate", format_datetime(datetime.fromisoformat(post["date"]).replace(tzinfo=timezone.utc)))]:
            SubElement(item, tag).text = value
        SubElement(item, "guid", isPermaLink="true").text = SITE + "/blogs/" + post["slug"]
    ElementTree(rss).write(BUILD / "rss.xml", encoding="utf-8", xml_declaration=True)
    sitemap = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for path in ["/", "/blog", "/gallery"] + ["/blogs/" + post["slug"] for post in posts]:
        SubElement(SubElement(sitemap, "url"), "loc").text = SITE + path
    ElementTree(sitemap).write(BUILD / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def build():
    posts = sorted(read_json("posts.json"), key=lambda post: post["date"], reverse=True)
    gallery = sorted(read_json("gallery.json"), key=lambda item: item.get("date", ""), reverse=True)
    years = sorted({post["date"][:4] for post in posts})
    year_range = "–".join(dict.fromkeys([years[0], years[-1]])) if years else ""
    # Fail before replacing the previous build if a source or asset is missing.
    required = [ROOT / name for name in ["index.html", "404.html", "_headers", "_redirects", "robots.txt",
                                         "resume/hassan_kamran_resume.pdf", "static/site.css", "static/site.js"]]
    required += [ROOT / "content/posts" / (p["slug"] + ".html") for p in posts]
    required += [ROOT / p["image"].lstrip("/") for p in posts]
    required += [ROOT / item["src"].lstrip("/") for item in gallery]
    for source in required:
        if not source.is_file():
            raise FileNotFoundError(f"Missing source: {source.relative_to(ROOT)}")
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()
    shutil.copytree(ROOT / "static", BUILD / "static")
    for name in ["favicon.ico", "favicon.svg", "favicon-192.png", "favicon-512.png", "apple-touch-icon.png", "site.webmanifest"]:
        shutil.copy2(ROOT / "static" / name, BUILD / name)
    for name in ["_headers", "_redirects", "robots.txt"]:
        shutil.copy2(ROOT / name, BUILD / name)
    shutil.copy2(ROOT / "resume/hassan_kamran_resume.pdf", BUILD / "hassan-kamran-resume.pdf")

    home = Template((ROOT / "index.html").read_text()).substitute(
        latest_posts="".join(post_row(p, preview=True) for p in posts[:3]),
        gallery_preview="".join(gallery_figure(item, preview=True) for item in gallery[:3]),
    )
    write_page("/", "Hassan Kamran — Engineer, Founder & Student",
               "The personal website of Hassan Kamran. Founder of Khan AI, mechatronics engineer, and MBA student. Work, writing, research, and a gallery.", home)
    write_page("/blog", "Blog — Hassan Kamran", "Notes on engineering, software, and things I’ve learned, by Hassan Kamran.",
               '<section class="page-heading"><p class="eyebrow">The blog</p><h1>Notes along the way.</h1>'
               '<p>Things I’ve built, ideas I’ve explored, and lessons worth writing down.</p></section>'
               f'<div class="archive-toolbar"><span>{len(posts)} articles · {year_range}</span><a href="/rss.xml">Follow via RSS ↗</a></div>'
               '<section class="archive" aria-label="All articles">' + "".join(post_row(p) for p in posts) + '</section>', section="blog")
    write_page("/gallery", "Gallery — Hassan Kamran", "A visual notebook of projects, research, and work by Hassan Kamran.",
               '<section class="page-heading"><p class="eyebrow">The gallery</p><h1>A visual notebook.</h1>'
               '<p>A few projects and moments from my work. Open any image for a closer look.</p></section>'
               '<div class="gallery-grid">' + "".join(gallery_figure(item) for item in gallery) + '</div>', section="gallery")
    for post in posts:
        body = (ROOT / "content/posts" / (post["slug"] + ".html")).read_text()
        note = ('<p class="archive-note">From the archive: this article describes an earlier version of this website.</p>'
                if post["slug"] in {"how-i-built-this-website", "static-site-generation-with-jinja2"} else "")
        article = (f'<article><header class="article-header"><a class="back-link" href="/blog">← All writing</a>'
                   f'{post_meta(post)}<h1>{escape(post["title"])}</h1>'
                   f'<p class="article-description">{escape(post["description"])}</p></header>'
                   f'<img class="article-image" src="{escape(post["image"])}" alt="" width="1120" height="460">'
                   f'<div class="prose">{note}{body}<div class="article-end">Written by Hassan Kamran. '
                   '<a href="/blog">More from the blog →</a></div></div></article>')
        write_page("/blogs/" + post["slug"], post["title"] + " — Hassan Kamran", post["description"], article, section="blog", article=True)
    write_page("/404", "Page not found — Hassan Kamran", "This page could not be found.", (ROOT / "404.html").read_text())
    write_feeds(posts)
    print(f"Built home, blog, gallery, {len(posts)} articles, RSS, and sitemap into {BUILD}")


if __name__ == "__main__":
    build()
