from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import re
import os
from datetime import datetime


class TemplateRenderer:
    """Simple template renderer wrapper"""

    def __init__(self, env, config):
        self.env = env
        self.config = config

    def inject_svg(
        self,
        svg_name: str,
        use_current_color: bool = False,
        classes: str = None,
        replace_none: bool = False,
    ) -> str:
        """Inject SVG with color processing - matches original logic"""
        svg_path = os.path.join(self.config.static_dir, f"{svg_name}.svg")

        if not os.path.exists(svg_path):
            return f"<!-- SVG '{svg_name}' not found -->"

        with open(svg_path, "r", encoding="utf-8") as file:
            svg_content = file.read()

        if use_current_color:
            # Your exact SVG processing logic from original
            svg_tag_match = re.search(r"<svg\s[^>]*>", svg_content)

            if svg_tag_match:
                svg_tag = svg_tag_match.group(0)
                svg_tag_end_pos = svg_tag_match.end()

                root_tag = svg_content[:svg_tag_end_pos]
                inner_content = svg_content[svg_tag_end_pos:]
                closing_tag_match = re.search(r"</svg>\s*$", inner_content)

                if closing_tag_match:
                    closing_tag_start_pos = closing_tag_match.start()
                    inner_content_only = inner_content[:closing_tag_start_pos]
                    closing_tag = inner_content[closing_tag_start_pos:]

                    # Process root tag
                    root_tag = re.sub(
                        r'fill="#[0-9a-fA-F]+"', 'fill="currentcolor"', root_tag
                    )
                    root_tag = re.sub(
                        r"fill='#[0-9a-fA-F]+'", "fill='currentcolor'", root_tag
                    )
                    root_tag = re.sub(
                        r'fill="rgb[a]?\([^)]+\)"', 'fill="currentcolor"', root_tag
                    )
                    root_tag = re.sub(
                        r'fill="(?!currentcolor|none)[a-zA-Z]+"',
                        'fill="currentcolor"',
                        root_tag,
                    )

                    # Process inner content
                    if replace_none:
                        inner_content_only = re.sub(
                            r'fill="none"', 'fill="currentcolor"', inner_content_only
                        )
                        inner_content_only = re.sub(
                            r"fill='none'", "fill='currentcolor'", inner_content_only
                        )
                        inner_content_only = re.sub(
                            r"fill=none", "fill=currentcolor", inner_content_only
                        )
                        inner_content_only = re.sub(
                            r'style="([^"]*?)fill:\s*none;([^"]*?)"',
                            r'style="\1fill:currentcolor;\2"',
                            inner_content_only,
                        )
                        inner_content_only = re.sub(
                            r"style='([^']*?)fill:\s*none;([^']*?)'",
                            r"style='\1fill:currentcolor;\2'",
                            inner_content_only,
                        )

                    # Always replace other colors
                    inner_content_only = re.sub(
                        r'fill="#[0-9a-fA-F]+"',
                        'fill="currentcolor"',
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r"fill='#[0-9a-fA-F]+'",
                        "fill='currentcolor'",
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r"fill=#[0-9a-fA-F]+", "fill=currentcolor", inner_content_only
                    )
                    inner_content_only = re.sub(
                        r'fill="rgb[a]?\([^)]+\)"',
                        'fill="currentcolor"',
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r"fill='rgb[a]?\([^)]+\)'",
                        "fill='currentcolor'",
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r'fill="(?!currentcolor)[a-zA-Z]+"',
                        'fill="currentcolor"',
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r"fill='(?!currentcolor)[a-zA-Z]+'",
                        "fill='currentcolor'",
                        inner_content_only,
                    )

                    # Handle inline style attributes
                    inner_content_only = re.sub(
                        r'style="([^"]*?)fill:[^;]+;([^"]*?)"',
                        r'style="\1fill:currentcolor;\2"',
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r"style='([^']*?)fill:[^;]+;([^']*?)'",
                        r"style='\1fill:currentcolor;\2'",
                        inner_content_only,
                    )

                    # Handle stroke attributes
                    if replace_none:
                        inner_content_only = re.sub(
                            r'stroke="none"',
                            'stroke="currentcolor"',
                            inner_content_only,
                        )
                        inner_content_only = re.sub(
                            r"stroke='none'",
                            "stroke='currentcolor'",
                            inner_content_only,
                        )
                        inner_content_only = re.sub(
                            r"stroke=none", "stroke=currentcolor", inner_content_only
                        )

                    inner_content_only = re.sub(
                        r'stroke="#[0-9a-fA-F]+"',
                        'stroke="currentcolor"',
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r"stroke='#[0-9a-fA-F]+'",
                        "stroke='currentcolor'",
                        inner_content_only,
                    )
                    inner_content_only = re.sub(
                        r'stroke="(?!currentcolor|none)[a-zA-Z]+"',
                        'stroke="currentcolor"',
                        inner_content_only,
                    )

                    svg_content = root_tag + inner_content_only + closing_tag

        if classes:
            svg_tag_match = re.search(r"<svg\s[^>]*>", svg_content)
            if svg_tag_match:
                svg_tag = svg_tag_match.group(0)
                if 'class="' in svg_tag:
                    new_svg_tag = re.sub(
                        r'class="([^"]*)"', f'class="\\1 {classes}"', svg_tag
                    )
                else:
                    new_svg_tag = svg_tag.replace(">", f' class="{classes}">')
                svg_content = svg_content.replace(svg_tag, new_svg_tag)

        return svg_content


def get_urls(depth=0):
    """Get URLs with proper relative paths based on depth"""
    prefix = "../" * depth
    return {
        "home": f"{prefix}index.html",
        "blog": f"{prefix}blog.html",
        "about": f"{prefix}about.html",
        "sitemap": f"{prefix}sitemap.xml",
        "image_sitemap": f"{prefix}sitemap-images.xml",
        "terms": f"{prefix}terms.html",
        "privacy": f"{prefix}privacy.html",
        "resume": f"{prefix}resume.html",
        "contact": f"{prefix}contact.html",
        "services_page": f"{prefix}services.html",
        "gallery": f"{prefix}gallery.html",
    }


class Page(ABC):
    """Base page class"""

    def __init__(self, renderer: TemplateRenderer):
        self.renderer = renderer
        self.config = renderer.config

    @property
    @abstractmethod
    def slug(self) -> str:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def template(self) -> str:
        pass

    @property
    @abstractmethod
    def output_path(self) -> Path:
        pass

    @property
    @abstractmethod
    def meta_description(self) -> str:
        pass

    @property
    def custom_css(self) -> Optional[str]:
        return None

    @property
    def preload(self) -> Optional[str]:
        return None

    def get_context(self) -> Dict[str, Any]:
        return {}

    def render(self) -> str:
        """Render page following original logic exactly"""
        # Calculate depth from output path
        page_name = str(self.output_path).replace(".html", "").replace("\\", "/")
        depth = page_name.count("/")

        # Get URLs adjusted for current page depth
        page_urls = get_urls(depth)

        # Calculate static path based on depth
        static_path = "../" * depth + "static"

        # Load templates
        base_template = self.renderer.env.get_template("base.html")
        content_template = self.renderer.env.get_template(self.template)

        # Prepare context
        context = self.get_context()
        context["inject_svg"] = (
            self.renderer.inject_svg
        )  # 👈 Ensure inject_svg is available

        # Render content template first with full context
        content = content_template.render(**context)

        # Prepare base template parameters
        comment_open = ""
        comment_close = ""
        if self.preload is None:
            comment_open = "<!--"
            comment_close = "-->"

        # Canonical URL
        if self.output_path.name == "index.html":
            canonical_url = f"{self.config.domain}/"
        else:
            # Handle paginated blog pages
            if hasattr(self, "is_paginated") and self.is_paginated:
                base_name = self.output_path.name.split("-")[0]
                canonical_url = f"{self.config.domain}/{base_name}.html"
            else:
                canonical_url = f"{self.config.domain}/{self.output_path}"

        # Remove any double slashes that might occur
        canonical_url = canonical_url.replace("//", "/").replace(":/", "://")

        canonical = f'<link rel="canonical" href="{canonical_url}" />'

        # Base template parameters (matching original)
        template_params = {
            "title": f"{self.config.base_title} | {self.title}",
            "content": content,  # 👈 Rendered HTML content
            "home": page_urls.get("home"),
            "blog": page_urls.get("blog"),
            "about": page_urls.get("about"),
            "sitemap": page_urls.get("sitemap"),
            "image_sitemap": page_urls.get("image_sitemap"),
            "privacy": page_urls.get("privacy"),
            "terms": page_urls.get("terms"),
            "resume": page_urls.get("resume"),
            "contact": page_urls.get("contact"),
            "services_page": page_urls.get("services_page"),
            "gallery": page_urls.get("gallery"),
            "preload": self.preload,
            "comment_open": comment_open,
            "comment_close": comment_close,
            "meta_des": self.meta_description,
            "static": static_path,
            "inject_svg": self.renderer.inject_svg,
            "copyright": datetime.now().year,
            "canonical": canonical,
            "custom_css": self.custom_css,
        }

        # Merge with any additional context
        template_params.update(context)

        # Render base template with all parameters
        return base_template.render(**template_params)
