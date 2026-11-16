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


def write_page(path, title, description, content, section="", article=False, author="Hassan Kamran"):
    output = BUILD / ("index.html" if path == "/" else path.lstrip("/") + ".html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(BASE.substitute(
        title=escape(title), description=escape(description), path=escape(path),
        content=content, year=date.today().year, author=escape(author),
        og_type="article" if article else "website",
        blog_current='aria-current="page"' if section == "blog" else "",
        gallery_current='aria-current="page"' if section == "gallery" else "",
    ))


def post_meta(post):
    published = date.fromisoformat(post["date"])
    return (f'<div class="post-meta"><span>{escape(post["category"])}</span>'
            f'{escape(post.get("date_label", ""))} '
            f'<time datetime="{post["date"]}">{published:%d %b %Y}</time></div>')


def post_row(post, preview=False):
    heading = "h3" if preview else "h2"
    description = "" if preview else f'<p>{escape(post["description"])}</p>'
    return (f'<a class="post-row" href="/blogs/{post["slug"]}"><div>'
            f'{post_meta(post)}<{heading}>{escape(post["title"])}</{heading}>'
            f'{description}</div><span class="post-arrow" aria-hidden="true">↗</span></a>')


def gallery_figure(item, preview=False):
    href = "/gallery" if preview else escape(item["src"])
    css = "" if preview else ' class="gallery-link"'
    caption = escape(item["title"])
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
    for post in sorted(posts, key=lambda post: post["date"], reverse=True):
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
    # JSON order is the editorial selection order; RSS remains chronological.
    posts = read_json("posts.json")
    gallery = read_json("gallery.json")
    # Fail before replacing the previous build if a source or asset is missing.
    required = [ROOT / name for name in ["index.html", "404.html", "_headers", "_redirects", "robots.txt",
                                         "resume/hassan_kamran_resume.pdf", "static/site.css", "static/site.js"]]
    required += [ROOT / "content/posts" / (p["slug"] + ".html") for p in posts]
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
        selected_posts="".join(post_row(p, preview=True) for p in posts[:3]),
        gallery_preview="".join(gallery_figure(item, preview=True) for item in gallery[:3]),
    )
    write_page("/", "Hassan Kamran — Engineer, Founder & Student",
               "The personal website of Hassan Kamran. Founder of Khan AI, mechatronics engineer, and MBA student. Work, writing, research, and a gallery.", home)
    write_page("/blog", "Blog — Hassan Kamran", "Selected project notes, research, and engineering writing from my work and time at Big0.",
               '<section class="page-heading"><p class="eyebrow">The blog</p><h1>Notes along the way.</h1>'
               '<p>Selected projects, research, and engineering notes from my own work and my time at Big0.</p></section>'
               f'<div class="archive-toolbar"><span>{len(posts)} selected pieces</span><a href="/rss.xml">Follow via RSS ↗</a></div>'
               '<section class="archive" aria-label="All articles">' + "".join(post_row(p) for p in posts) + '</section>', section="blog")
    write_page("/gallery", "Gallery — Hassan Kamran", "Photographs from talks, university visits, and events during my time at Big0.",
               '<section class="page-heading"><p class="eyebrow">The gallery</p><h1>People &amp; places.</h1>'
               '<p>Talks, university visits, and conversations from my time at Big0. Open a photograph for a closer look.</p></section>'
               '<div class="gallery-grid">' + "".join(gallery_figure(item) for item in gallery) + '</div>', section="gallery")
    for post in posts:
        body = (ROOT / "content/posts" / (post["slug"] + ".html")).read_text()
        note = ('<p class="archive-note">From the archive: this article describes an earlier version of this website.</p>'
                if post["slug"] == "how-i-built-this-website" else "")
        credit = escape(post["credit"])
        if post.get("source_url"):
            credit += f' <a href="{escape(post["source_url"])}">{escape(post["source_title"])}</a>.'
        article = (f'<article><header class="article-header"><a class="back-link" href="/blog">← All writing</a>'
                   f'{post_meta(post)}<h1>{escape(post["title"])}</h1>'
                   f'<p class="article-description">{escape(post["description"])}</p>'
                   f'<p class="article-credit">{credit}</p></header>'
                   f'<div class="prose">{note}{body}<div class="article-end">'
                   '<a href="/blog">More from the blog →</a></div></div></article>')
        write_page("/blogs/" + post["slug"], post["title"] + " — Hassan Kamran", post["description"], article,
                   section="blog", article=True, author=post.get("author", "Hassan Kamran"))
    write_page("/404", "Page not found — Hassan Kamran", "This page could not be found.", (ROOT / "404.html").read_text())
    write_feeds(posts)
    print(f"Built home, blog, gallery, {len(posts)} articles, RSS, and sitemap into {BUILD}")


if __name__ == "__main__":
    build()
