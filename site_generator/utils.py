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
    """Generate image sitemap XML by scanning rendered page content"""
    images = []
    seen_images = set()  # Prevent duplicates

    def escape_xml(text):
        """Escape XML special characters"""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def normalize_image_url(src, base_url):
        """Normalize image URL to absolute URL"""
        if src.startswith(("http://", "https://")):
            return src

        # Clean relative paths
        src = src.replace("../", "").replace("./", "").lstrip("/")
        return f"{base_url}/{src}"

    def get_page_url(page, config):
        """Get the canonical page URL"""
        if page.output_path.name == "index.html":
            return f"{config.domain}/"
        else:
            # Handle paginated pages
            if (
                hasattr(page, "is_paginated")
                and page.is_paginated
                and hasattr(page, "page_num")
            ):
                if page.page_num == 1:
                    # First page of pagination uses base name
                    base_name = str(page.output_path).split("-")[0] + ".html"
                    return f"{config.domain}/{base_name}"

            return f"{config.domain}/{page.output_path}"

    def extract_images_from_context(context, page_url, page_title):
        """Extract images from page context"""
        image_sources = []

        # Check for blog posts with images
        if "blog_posts" in context:
            for post in context["blog_posts"]:
                if "image_url" in post:
                    img_src = post["image_url"]
                    alt_text = post.get("title", post.get("meta_des", ""))
                    image_sources.append((img_src, alt_text))

        # Check for services with images
        if "services" in context:
            for service in context["services"]:
                if hasattr(service, "image") and service.image:
                    img_src = f"./static/{service.image}"
                    alt_text = service.title
                    image_sources.append((img_src, alt_text))

        # Check for gallery images
        if "images" in context:
            for img in context["images"]:
                if hasattr(img, "filename"):
                    img_src = f"./content/gallery/{img.filename}"
                    alt_text = img.title
                    image_sources.append((img_src, alt_text))

        # Check for individual context values that might be images
        image_keys = ["hero", "image", "profile_image", "background_image"]
        for key in image_keys:
            if key in context and context[key]:
                img_value = context[key]
                # Handle different image formats
                if isinstance(img_value, str):
                    # Check if it looks like an image filename
                    if any(
                        img_value.lower().endswith(ext)
                        for ext in [
                            ".jpg",
                            ".jpeg",
                            ".png",
                            ".gif",
                            ".webp",
                            ".avif",
                            ".svg",
                        ]
                    ):
                        img_src = f"./static/{img_value}"
                        alt_text = f"{page_title} {key.replace('_', ' ')}"
                        image_sources.append((img_src, alt_text))

        # Check for any other string values in context that look like image paths
        for key, value in context.items():
            if isinstance(value, str) and value:
                # Skip known non-image keys
                skip_keys = [
                    "title",
                    "content",
                    "meta_des",
                    "static",
                    "copyright",
                    "canonical",
                    "custom_css",
                ]
                if key in skip_keys:
                    continue

                # Check if value looks like an image filename or path
                if any(
                    value.lower().endswith(ext)
                    for ext in [
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".webp",
                        ".avif",
                        ".svg",
                    ]
                ):
                    # Determine the appropriate path prefix
                    if value.startswith("static/") or value.startswith("./static/"):
                        img_src = f"./{value}" if not value.startswith("./") else value
                    else:
                        img_src = f"./static/{value}"

                    alt_text = f"{page_title} {key.replace('_', ' ')}"
                    image_sources.append((img_src, alt_text))

        return image_sources

    # Process each page's rendered content
    for page in pages:
        try:
            # Skip 404 and other non-indexable pages
            if hasattr(page, "slug") and page.slug in ["404"]:
                continue

            # Get page content from the rendered page context
            page_url = get_page_url(page, config)
            context = page.get_context()

            # Extract images from context
            image_sources = extract_images_from_context(context, page_url, page.title)

            # Check for preload hero images
            if hasattr(page, "preload") and page.preload:
                # This indicates a hero image
                img_src = f"./static/{page.preload}.avif"  # Assuming avif format
                alt_text = f"{page.title} hero image"
                image_sources.append((img_src, alt_text))

            # Process found images
            for img_src, alt_text in image_sources:
                if img_src:
                    # Normalize the image URL
                    normalized_url = normalize_image_url(img_src, config.domain)

                    # Create unique identifier to prevent duplicates
                    image_key = (page_url, normalized_url)

                    if image_key not in seen_images:
                        seen_images.add(image_key)

                        images.append(f"""  <url>
    <loc>{page_url}</loc>
    <image:image>
      <image:loc>{normalized_url}</image:loc>
      <image:title>{escape_xml(alt_text)}</image:title>
    </image:image>
  </url>""")

        except Exception as e:
            print(f"Error processing page {page.output_path}: {e}")

    if not images:
        return ""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(images)}
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
