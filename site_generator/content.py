from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import markdown
import os
from bs4 import BeautifulSoup
import json

from .core import Page, TemplateRenderer


@dataclass
class ContentItem:
    """Base class for content items"""

    slug: str
    title: str
    content_html: str
    meta_description: str = ""


@dataclass
class BlogPost(ContentItem):
    category: str = "Uncategorized"
    date: datetime = None
    image: str = None

    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now()


@dataclass
class Service(ContentItem):
    icon: str = None
    price: str = None
    features: List[str] = None


@dataclass
class GalleryImage:
    filename: str
    title: str
    description: str = ""
    category: str = ""


class ContentLoader:
    """Loads content from markdown/text files"""

    def __init__(self, config):
        self.config = config
        self.md = markdown.Markdown(extensions=["extra", "codehilite"])

    def load_blog_posts(self) -> List[BlogPost]:
        """Load blog posts from markdown/txt files with enhanced detection"""
        posts = []
        blog_dir = Path(self.config.blog_dir)
        seen_slugs = set()
        error_count = 0
        processed_count = 0
        skipped_files = []

        if not blog_dir.exists():
            print(f"❌ Blog directory not found: {blog_dir}")
            return posts

        print(f"📂 Scanning blog directory: {blog_dir}")

        # Get all potential blog files (case-insensitive)
        all_files = []
        for file_path in blog_dir.iterdir():
            if file_path.is_file():
                # Case-insensitive extension check
                if file_path.suffix.lower() in [".md", ".txt"]:
                    all_files.append(file_path)
                else:
                    skipped_files.append((file_path.name, "Invalid extension"))

        print(f"📋 Found {len(all_files)} potential blog files")

        for file_path in sorted(all_files):
            filename = file_path.name
            print(f"🔍 Processing {filename}...")

            try:
                # Read file with multiple encoding attempts
                content = None
                for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                    try:
                        content = file_path.read_text(encoding=encoding).strip()
                        break
                    except UnicodeDecodeError:
                        continue

                if content is None:
                    print(f"❌ Could not decode {filename} with any encoding")
                    skipped_files.append((filename, "Encoding error"))
                    error_count += 1
                    continue

                if not content:
                    print(f"⚠️ Empty file skipped: {filename}")
                    skipped_files.append((filename, "Empty file"))
                    error_count += 1
                    continue

                lines = content.split("\n")
                if len(lines) < 5:
                    print(
                        f"⚠️ Insufficient metadata in {filename} (found {len(lines)} lines, need 5)"
                    )
                    skipped_files.append((filename, f"Only {len(lines)} lines"))
                    error_count += 1
                    continue

                # Enhanced slug normalization
                base_name = file_path.stem  # Use stem instead of splitext
                slug = self._normalize_slug(base_name)

                # Validate slug uniqueness
                if slug in seen_slugs:
                    # Try to make unique by appending number
                    original_slug = slug
                    counter = 2
                    while f"{slug}-{counter}" in seen_slugs:
                        counter += 1
                    slug = f"{slug}-{counter}"
                    print(f"🔄 Duplicate slug '{original_slug}' renamed to '{slug}'")

                seen_slugs.add(slug)

                # Parse metadata with better error handling
                try:
                    title = lines[0].strip() or "Untitled Post"
                    category = lines[1].strip() if len(lines) > 1 else "Uncategorized"
                    date_str = lines[2].strip() if len(lines) > 2 else ""
                    img_name = lines[3].strip() if len(lines) > 3 else ""
                    meta_des = lines[4].strip() if len(lines) > 4 else ""

                    # Validate and clean image name
                    if img_name and not img_name.lower().endswith(
                        (".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif")
                    ):
                        print(f"⚠️ Invalid image extension in {filename}: {img_name}")
                        img_name = ""

                except Exception as e:
                    print(f"⚠️ Metadata parsing error in {filename}: {str(e)}")
                    skipped_files.append((filename, "Metadata parsing error"))
                    error_count += 1
                    continue

                # Enhanced date parsing
                post_date = self._parse_date(date_str)
                if not post_date:
                    print(
                        f"ℹ️ Invalid date '{date_str}' in {filename}, using current date"
                    )
                    post_date = datetime.now()

                # Content processing
                markdown_content = "\n".join(lines[5:]) if len(lines) > 5 else ""

                # Reset markdown instance for each file to avoid state issues
                self.md.reset()

                try:
                    html_content = self.md.convert(markdown_content)
                    cleaned_html = self._process_blog_html(html_content)
                except Exception as e:
                    print(f"⚠️ Markdown conversion error in {filename}: {str(e)}")
                    skipped_files.append((filename, "Markdown conversion error"))
                    error_count += 1
                    continue

                # Create blog post object
                posts.append(
                    BlogPost(
                        slug=slug,
                        title=title,
                        category=category,
                        date=post_date,
                        content_html=cleaned_html,
                        image=img_name,
                        meta_description=meta_des[:160]
                        if meta_des
                        else title[:160],  # Limit meta description length
                    )
                )
                processed_count += 1
                print(f"✅ Successfully processed: {filename} -> {slug}")

            except Exception as e:
                print(f"❌ Critical error processing {filename}: {str(e)}")
                skipped_files.append((filename, f"Critical error: {str(e)}"))
                error_count += 1

        # Final reporting
        posts.sort(key=lambda p: p.date, reverse=True)
        print(f"\n📊 Blog Loading Summary:")
        print(f"✅ Successfully processed: {processed_count} posts")
        print(f"⛔ Errors encountered: {error_count}")
        print(f"📁 Total files scanned: {len(all_files)}")

        if skipped_files:
            print(f"\n⚠️ Skipped files:")
            for name, reason in skipped_files:
                print(f"  - {name}: {reason}")

        return posts

    def _normalize_slug(self, text: str) -> str:
        """Normalize text to create a valid slug"""
        import re

        # Convert to lowercase
        slug = text.lower().strip()

        # Replace spaces and special characters with hyphens
        slug = re.sub(r"[^\w\s-]", "", slug)  # Remove special chars except hyphens
        slug = re.sub(
            r"[-\s]+", "-", slug
        )  # Replace spaces and multiple hyphens with single hyphen

        # Remove leading/trailing hyphens
        slug = slug.strip("-")

        # Limit length
        if len(slug) > 100:
            slug = slug[:100].rsplit("-", 1)[0]  # Cut at last hyphen before 100 chars

        return slug or "untitled"  # Fallback if slug is empty

    def load_services(self) -> List[Service]:
        """Load services from markdown files"""
        services = []
        services_dir = Path(self.config.services_dir)

        if not services_dir.exists():
            print(f"Services directory not found: {services_dir}")
            return services

        for filename in os.listdir(services_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(services_dir, filename)
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read().strip()

                    if not content:
                        continue

                    # Parse front matter
                    metadata = {}
                    markdown_content = content

                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            for line in parts[1].strip().split("\n"):
                                if ":" in line:
                                    key, value = line.split(":", 1)
                                    metadata[key.strip()] = value.strip()
                            markdown_content = parts[2]

                    # Convert to HTML
                    html_content = self.md.convert(markdown_content)

                    service = Service(
                        slug=os.path.splitext(filename)[0],
                        title=metadata.get("title", "Untitled Service"),
                        content_html=html_content,
                        meta_description=metadata.get("description", ""),
                        icon=metadata.get("icon"),
                        price=metadata.get("price"),
                        features=[
                            f.strip() for f in metadata.get("features", "").split(",")
                        ]
                        if metadata.get("features")
                        else [],
                    )
                    services.append(service)

        return services

    def load_gallery_images(self) -> List[GalleryImage]:
        images = []
        gallery_dir = Path(self.config.gallery_dir)

        # Add metadata.json check if using
        for filename in os.listdir(gallery_dir):
            if filename.lower().endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif")
            ):
                title = filename.replace("-", " ").replace("_", " ").title()
                images.append(
                    GalleryImage(
                        filename=filename,
                        title=title,
                        description="",  # Populate from metadata if available
                        category="",
                    )
                )
        return images

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date from various formats"""
        if not date_str:
            return datetime.now()

        formats = ["%Y-%m-%d", "%B %d, %Y", "%d %B %Y", "%d/%m/%Y", "%m/%d/%Y"]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return datetime.now()

    def _process_blog_html(self, html: str) -> str:
        """Process blog HTML content"""
        soup = BeautifulSoup(html, "html.parser")

        # Fix image paths
        for img in soup.find_all("img"):
            if img.get("src") and img["src"].startswith("static/"):
                img["src"] = "../" + img["src"]

        # Add classes to tables
        for table in soup.find_all("table"):
            table["class"] = table.get("class", []) + ["blog-table"]

        return str(soup)


class BlogPostPage(Page):
    """Individual blog post page"""

    def __init__(self, renderer: TemplateRenderer, post: BlogPost):
        super().__init__(renderer)
        self.post = post

    @property
    def slug(self) -> str:
        return f"blog-{self.post.slug}"

    @property
    def title(self) -> str:
        return self.post.title

    @property
    def template(self) -> str:
        return "blog_post.html"

    @property
    def output_path(self) -> Path:
        return Path(f"blogs/{self.post.slug}.html")

    @property
    def meta_description(self) -> str:
        return self.post.meta_description

    def get_context(self) -> Dict[str, Any]:
        return {
            "title": self.post.title,
            "category": self.post.category,
            "date": self.post.date.strftime("%B %d, %Y"),
            "blog_content": self.post.content_html,
            "meta_des": self.post.meta_description,
        }


class ServicePage(Page):
    """Individual service page"""

    def __init__(self, renderer: TemplateRenderer, service: Service):
        super().__init__(renderer)
        self.service = service

    @property
    def slug(self) -> str:
        return f"service-{self.service.slug}"

    @property
    def title(self) -> str:
        return self.service.title

    @property
    def template(self) -> str:
        return "service_detail.html"

    @property
    def output_path(self) -> Path:
        return Path(f"services/{self.service.slug}.html")

    @property
    def meta_description(self) -> str:
        return self.service.meta_description

    def get_context(self) -> Dict[str, Any]:
        return {"service": self.service, "content": self.service.content_html}


class BlogListingPage(Page):
    """Blog listing page with pagination"""

    def __init__(
        self,
        renderer: TemplateRenderer,
        posts: List[BlogPost],
        page_num: int = 1,
        total_pages: int = 1,
    ):
        super().__init__(renderer)
        self.posts = posts
        self.page_num = page_num
        self.total_pages = total_pages

    @property
    def slug(self) -> str:
        return "blog" if self.page_num == 1 else f"blog-{self.page_num}"

    @property
    def is_paginated(self) -> bool:
        return self.total_pages > 1

    @property
    def title(self) -> str:
        return "Blog" if self.page_num == 1 else f"Blog - Page {self.page_num}"

    @property
    def template(self) -> str:
        return "blog.html"

    @property
    def output_path(self) -> Path:
        return (
            Path("blog.html")
            if self.page_num == 1
            else Path(f"blog-{self.page_num}.html")
        )

    @property
    def meta_description(self) -> str:
        return "Explore cutting-edge insights on AI, Federated Learning, programming, big data, and robotics."

    def get_context(self) -> Dict[str, Any]:
        # Format blog posts for template
        blog_posts = []
        for post in self.posts:
            blog_posts.append(
                {
                    "title": post.title,
                    "category": post.category,
                    "date": post.date.strftime("%B %d, %Y"),
                    "filename": f"./blogs/{post.slug}.html",
                    "image_url": f"./static/{post.image}"
                    if post.image
                    else "./static/default.jpg",
                    "meta_des": post.meta_description,
                }
            )

        context = {"blog_posts": blog_posts}

        if self.total_pages > 1:
            context["pagination"] = {
                "current_page": self.page_num,
                "total_pages": self.total_pages,
                "has_prev": self.page_num > 1,
                "has_next": self.page_num < self.total_pages,
                "prev_url": "./blog.html"
                if self.page_num == 2
                else f"./blog-{self.page_num - 1}.html",
                "next_url": f"./blog-{self.page_num + 1}.html",
            }

        return context
