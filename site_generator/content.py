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
        """Load blog posts from text/markdown files"""
        posts = []
        blog_dir = Path(self.config.blog_dir)

        if not blog_dir.exists():
            return posts

        # Process .md files (matching original format)
        for filename in os.listdir(blog_dir):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(blog_dir, filename)
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read().strip()

                    if not content:
                        print(f"Skipping empty blog file: {filename}")
                        continue

                    # Parse metadata from file (original format)
                    lines = content.split("\n")
                    title = lines[0].strip()
                    category = lines[1].strip() if len(lines) > 1 else "Uncategorized"
                    date_str = lines[2].strip() if len(lines) > 2 else "Unknown date"
                    img_name = lines[3].strip() if len(lines) > 3 else ""
                    meta_des = lines[4].strip() if len(lines) > 4 else ""

                    # Extract markdown content
                    markdown_content = "\n".join(lines[5:]) if len(lines) > 5 else ""

                    # Convert to HTML
                    html_content = self.md.convert(markdown_content)
                    html_content = self._process_blog_html(html_content)

                    # Get filename without extension
                    post_filename = os.path.splitext(filename)[0]

                    post = BlogPost(
                        slug=post_filename,
                        title=title,
                        category=category,
                        date=self._parse_date(date_str),
                        content_html=html_content,
                        image=img_name,
                        meta_description=meta_des,
                    )
                    posts.append(post)

        # Sort by date (newest first)
        posts.sort(key=lambda p: p.date, reverse=True)
        return posts

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
