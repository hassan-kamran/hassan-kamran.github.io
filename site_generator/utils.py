# Updated utils.py imports
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json
import shutil
from bs4 import BeautifulSoup
from .core import Page  # 👈 Add this
from .content import BlogPost, Service  # 👈 Add these


def ensure_directory(path: Path) -> None:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str) -> None:
    """Write content to file"""
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")


def generate_sitemap(pages: List, config) -> str:
    """Generate XML sitemap"""
    urls = []

    for page in pages:
        # Skip certain pages
        if hasattr(page, "slug") and page.slug in ["404"]:
            continue

        if page.output_path == Path("index.html"):
            loc = f"{config.domain}/"
        else:
            loc = f"{config.domain}/{page.output_path}"

        priority = (
            "1.0"
            if page.slug == "index"
            else "0.8"
            if page.slug.startswith("blog-")
            else "0.7"
        )

        urls.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <priority>{priority}</priority>
  </url>""")

    # Add PDF resume
    urls.append(f"""  <url>
    <loc>{config.domain}/static/hassan_resume.pdf</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <priority>0.6</priority>
  </url>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""


def generate_image_sitemap(pages: List[Page], config) -> str:
    """Generate image sitemap XML by scanning ALL pages for images"""
    images = []

    for page in pages:
        if hasattr(page, "output_path"):
            html_path = Path(config.output_dir) / page.output_path
            if html_path.exists() and html_path.suffix == ".html":
                try:
                    soup = BeautifulSoup(html_path.read_text(), "html.parser")
                    for img in soup.find_all("img"):
                        src = img.get("src", "")
                        if src and not src.startswith(("http://", "https://")):
                            # Clean relative paths and construct absolute URL
                            src = src.replace("../", "").lstrip("/")
                            img_url = f"{config.domain}/{src}"

                            images.append(f"""  <url>
    <loc>{config.domain}/{page.output_path}</loc>
    <image:image>
      <image:loc>{img_url}</image:loc>
      <image:title>{img.get("alt", "")}</image:title>
    </image:image>
  </url>""")
                except Exception as e:
                    print(f"Error processing {html_path}: {e}")

    if not images:
        return ""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(set(images))}
</urlset>"""


def generate_robots_txt(config) -> str:
    """Generate robots.txt"""
    return f"""# robots.txt for {config.domain}
User-agent: *
Allow: /

Sitemap: {config.domain}/sitemap.xml
Sitemap: {config.domain}/sitemap-images.xml"""


def generate_search_index(
    pages: List[Page], blog_posts: List[BlogPost], services: List[Service]
) -> str:
    """Generate search index JSON with duplicate protection"""
    documents = []
    seen_ids = set()

    def add_document(doc: dict):
        """Safely add document with duplicate checking"""
        if doc["id"] in seen_ids:
            print(f"⚠️ Skipping duplicate ID: {doc['id']}")
            return
        seen_ids.add(doc["id"])
        documents.append(doc)

    # Add static pages (excluding blog post pages)
    for page in pages:
        if hasattr(page, "slug") and page.slug not in ["404"]:
            # Skip blog post pages and service pages (they're handled separately)
            if "blog/" in str(page.output_path) or "services/" in str(page.output_path):
                continue

            add_document(
                {
                    "id": f"page-{page.slug}",
                    "url": str(page.output_path),
                    "title": page.title,
                    "content": "",
                    "description": page.meta_description,
                    "type": "page",
                }
            )

    # Add blog posts directly from content
    for post in blog_posts:
        add_document(
            {
                "id": f"blog-{post.slug}",
                "url": f"blogs/{post.slug}.html",
                "title": post.title,
                "content": post.meta_description,
                "description": post.meta_description,
                "type": "blog",
                "category": post.category,
                "date": post.date.strftime("%Y-%m-%d"),
            }
        )

    # Add services directly from content
    for service in services:
        add_document(
            {
                "id": f"service-{service.slug}",
                "url": f"services/{service.slug}.html",
                "title": service.title,
                "content": service.meta_description,
                "description": service.meta_description,
                "type": "service",
            }
        )

    # Save to static directory
    output_path = Path("static/search-index.json")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(documents, indent=2))

    print(f"✅ Generated search index with {len(documents)} entries")
    return json.dumps(documents, indent=2)


def create_redirect_page(old_url: str, new_url: str, domain: str) -> str:
    """Create redirect HTML"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <link rel="canonical" href="{domain}{new_url}">
    <meta http-equiv="refresh" content="0;url={new_url}">
    <script>window.location.href = "{new_url}";</script>
</head>
<body>
    <h1>Redirecting...</h1>
    <p>This page has moved. If you are not redirected automatically, <a href="{new_url}">click here</a>.</p>
</body>
</html>"""
