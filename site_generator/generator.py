import shutil
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import os

from .config import Config
from .core import TemplateRenderer
from .pages import *
from .content import (
    ContentLoader,
    BlogPostPage,
    ServicePage,
    BlogListingPage,
    GalleryListingPage,
)
from .utils import *


class SiteGenerator:
    """Simple site generator"""

    def __init__(self, config: Config):
        """Initialize the site generator"""
        self.config = config
        self.pages: List[Page] = []
        self.blog_posts = []
        self.services = []
        self.gallery_images = []

        # Setup Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(config.templates_dir),
            autoescape=select_autoescape(
                enabled_extensions=("html",), default_for_string=True
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Create renderer
        self.renderer = TemplateRenderer(env, config)

        # Create content loader with renderer
        self.content_loader = ContentLoader(config, self.renderer)

    def generate(self):
        """Generate the website"""
        print("Starting website generation...")

        # Clean output directories
        self._clean_output()

        # Load content
        self.blog_posts = self.content_loader.load_blog_posts()
        self.services = self.content_loader.load_services()
        self.gallery_images = self.content_loader.load_gallery_images()

        print(f"Loaded {len(self.blog_posts)} blog posts")
        print(f"Loaded {len(self.services)} services")
        print(f"Loaded {len(self.gallery_images)} gallery images")

        # Create all pages
        self._create_static_pages()
        self._create_blog_pages()
        self._create_service_pages()
        self._create_gallery_pages()  # NEW: Add gallery pages with pagination

        # Render all pages
        for page in self.pages:
            output_path = Path(self.config.output_dir) / page.output_path

            # Only create directories if needed (prevent empty string path)
            if str(output_path.parent) != ".":
                os.makedirs(output_path.parent, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as file:
                file.write(page.render())

        # Generate sitemaps
        self._generate_sitemap()
        self._generate_image_sitemap()

        # Generate robots.txt
        self._generate_robots()

        # Generate search index
        self._generate_search_index()

        # Create redirects
        self._create_redirects()

        print(f"Website generation complete! Generated {len(self.pages)} pages.")

    def _clean_output(self):
        """Clean output directories"""
        if os.path.exists("./blogs"):
            shutil.rmtree("./blogs")
        os.mkdir("./blogs")

        if os.path.exists("./services"):
            shutil.rmtree("./services")
        os.mkdir("./services")

    def _create_static_pages(self):
        """Create static pages"""
        # Standard pages (NO GalleryPage here anymore)
        static_page_classes = [
            HomePage,
            AboutPage,
            ResumePage,
            ContactPage,
            PrivacyPage,
            TermsPage,
            NotFoundPage,
        ]

        for page_class in static_page_classes:
            self.pages.append(page_class(self.renderer))

        # Services page with data
        services_page = ServicesPage(self.renderer)
        services_page.set_services(self.services)
        self.pages.append(services_page)

    def _create_blog_pages(self):
        """Create blog-related pages"""
        if not self.blog_posts:
            return

        # Individual blog posts
        for post in self.blog_posts:
            self.pages.append(BlogPostPage(self.renderer, post))

        # Paginated blog listing
        posts_per_page = self.config.posts_per_page
        total_pages = (len(self.blog_posts) + posts_per_page - 1) // posts_per_page

        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * posts_per_page
            end = min(start + posts_per_page, len(self.blog_posts))
            page_posts = self.blog_posts[start:end]

            self.pages.append(
                BlogListingPage(self.renderer, page_posts, page_num, total_pages)
            )

    def _create_service_pages(self):
        """Create service-related pages"""
        if not self.services:
            return

        # Individual service pages
        for service in self.services:
            self.pages.append(ServicePage(self.renderer, service))

    def _generate_sitemap(self):
        """Generate sitemap.xml"""
        pages = []

        for page in self.pages:
            if hasattr(page, "slug") and page.slug != "404":
                if page.output_path == Path("index.html"):
                    loc = f"{self.config.domain}/"
                else:
                    loc = f"{self.config.domain}/{page.output_path}"

                priority = (
                    "1.0"
                    if page.slug == "index"
                    else "0.8"
                    if not page.slug.startswith("blog-")
                    else "0.7"
                )

                pages.append(
                    {
                        "loc": loc,
                        "lastmod": datetime.now().strftime("%Y-%m-%d"),
                        "priority": priority,
                    }
                )

        # Add PDF resume
        pages.append(
            {
                "loc": f"{self.config.domain}/static/hassan_resume.pdf",
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "priority": "0.6",
            }
        )

        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += (
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        )

        for page in pages:
            sitemap_content += "  <url>\n"
            sitemap_content += f"    <loc>{page['loc']}</loc>\n"
            sitemap_content += f"    <lastmod>{page['lastmod']}</lastmod>\n"
            sitemap_content += f"    <priority>{page['priority']}</priority>\n"
            sitemap_content += "  </url>\n"

        sitemap_content += "</urlset>"

        with open("./sitemap.xml", "w", encoding="utf-8") as file:
            file.write(sitemap_content)

    def _create_gallery_pages(self):
        """Create gallery-related pages with pagination"""
        if not self.gallery_images:
            # Create empty gallery page even if no images
            self.pages.append(GalleryListingPage(self.renderer, [], 1, 1))
            return

        # Paginated gallery listing
        imgs_per_page = self.config.gallery_imgs_per_page
        total_pages = (len(self.gallery_images) + imgs_per_page - 1) // imgs_per_page

        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * imgs_per_page
            end = min(start + imgs_per_page, len(self.gallery_images))
            page_images = self.gallery_images[start:end]

            self.pages.append(
                GalleryListingPage(self.renderer, page_images, page_num, total_pages)
            )

        print(f"✅ Created {total_pages} gallery pages")

    def _generate_image_sitemap(self):
        """Generate image sitemap including ALL images from all pages"""
        from .utils import generate_image_sitemap

        sitemap_content = generate_image_sitemap(self.pages, self.config)

        if sitemap_content:
            with open("./sitemap-images.xml", "w", encoding="utf-8") as file:
                file.write(sitemap_content)

    def _generate_robots(self):
        """Generate robots.txt"""
        robots_content = f"# robots.txt for {self.config.domain}\n"
        robots_content += "User-agent: *\n"
        robots_content += "Allow: /\n\n"
        robots_content += f"Sitemap: {self.config.domain}/sitemap.xml\n"
        robots_content += "Disallow: /cdn-cgi/\n"

        if self.gallery_images:
            robots_content += f"Sitemap: {self.config.domain}/sitemap-images.xml\n"

        with open("./robots.txt", "w", encoding="utf-8") as file:
            file.write(robots_content)

    def _generate_search_index(self):
        """Generate search index"""
        from .utils import generate_search_index

        # Corrected call with proper parameters
        generate_search_index(
            pages=self.pages, blog_posts=self.blog_posts, services=self.services
        )

    def _create_redirects(self):
        """Create basic redirect pages"""
        print("Creating redirects...")

        for old_url, new_url in self.config.redirects.items():
            output_path = Path(self.config.output_dir) / old_url
            output_dir = output_path.parent

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Create redirect HTML
            redirect_html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Redirecting...</title>
        <link rel="canonical" href="{self.config.domain}{new_url}">
        <meta http-equiv="refresh" content="0;url={new_url}">
        <script>window.location.href = "{new_url}";</script>
    </head>
    <body>
        <h1>Redirecting...</h1>
        <p>This page has moved. If you are not redirected automatically, <a href="{new_url}">click here</a>.</p>
    </body>
    </html>"""

            with open(output_path, "w", encoding="utf-8") as file:
                file.write(redirect_html)

            print(f"✅ Created redirect: {old_url} → {new_url}")
