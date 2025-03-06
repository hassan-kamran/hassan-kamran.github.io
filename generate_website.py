from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import re
import markdown
import shutil
import json
from bs4 import BeautifulSoup

from generate_search_index import generate_search_index

TEMPLATES_FOLDER = "./templates"
BASE_TEMPLATE = "base.html"
BLOG_FOLDER = "./text"
SVG_FOLDER = "./static"
SEARCH_INDEX_FILE = "./static/search-index.json"


def get_urls(depth=0):
    prefix = "../" * depth
    return {
        "home": f"{prefix}index.html",
        "blog": f"{prefix}blog.html",
        "about": f"{prefix}about.html",
        "sitemap": f"{prefix}sitemap.xml",
    }


env = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER))


def inject_svg(svg_name, use_current_color=False, classes=None, replace_none=False):
    svg_path = os.path.join(SVG_FOLDER, f"{svg_name}.svg")

    # Check if the SVG file exists
    if not os.path.exists(svg_path):
        return f"<!-- SVG '{svg_name}' not found -->"

    # Read the SVG file
    with open(svg_path, "r", encoding="utf-8") as file:
        svg_content = file.read()

    if use_current_color:
        # First find the root SVG tag
        svg_tag_match = re.search(r"<svg\s[^>]*>", svg_content)

        if svg_tag_match:
            svg_tag = svg_tag_match.group(0)
            svg_tag_end_pos = svg_tag_match.end()

            # Split the SVG into the root tag and the content
            root_tag = svg_content[:svg_tag_end_pos]
            inner_content = svg_content[svg_tag_end_pos:]
            closing_tag_match = re.search(r"</svg>\s*$", inner_content)

            if closing_tag_match:
                closing_tag_start_pos = closing_tag_match.start()
                inner_content_only = inner_content[:closing_tag_start_pos]
                closing_tag = inner_content[closing_tag_start_pos:]

                # Process the root tag - replace colors but NOT none
                # Replace fill="#hexcode" with fill="currentcolor" in root tag
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

                # Process inner content - replace all colors including none if replace_none is True
                if replace_none:
                    # Replace fill="none" with fill="currentcolor" in child elements
                    inner_content_only = re.sub(
                        r'fill="none"', 'fill="currentcolor"', inner_content_only
                    )
                    inner_content_only = re.sub(
                        r"fill='none'", "fill='currentcolor'", inner_content_only
                    )
                    inner_content_only = re.sub(
                        r"fill=none", "fill=currentcolor", inner_content_only
                    )

                    # Replace inline style with fill:none
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

                # Always replace other colors in inner content
                inner_content_only = re.sub(
                    r'fill="#[0-9a-fA-F]+"', 'fill="currentcolor"', inner_content_only
                )
                inner_content_only = re.sub(
                    r"fill='#[0-9a-fA-F]+'", "fill='currentcolor'", inner_content_only
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

                # Handle inline style attributes with fill
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

                # Also handle stroke attributes
                if replace_none:
                    inner_content_only = re.sub(
                        r'stroke="none"', 'stroke="currentcolor"', inner_content_only
                    )
                    inner_content_only = re.sub(
                        r"stroke='none'", "stroke='currentcolor'", inner_content_only
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

                # Reassemble the SVG
                svg_content = root_tag + inner_content_only + closing_tag

    # Add CSS classes if provided
    if classes:
        # Find the opening SVG tag
        svg_tag_match = re.search(r"<svg\s[^>]*>", svg_content)
        if svg_tag_match:
            svg_tag = svg_tag_match.group(0)

            # Check if the SVG already has a class attribute
            if 'class="' in svg_tag:
                # Append to existing class attribute
                new_svg_tag = re.sub(
                    r'class="([^"]*)"', f'class="\\1 {classes}"', svg_tag
                )
            else:
                # Add new class attribute before the closing '>'
                new_svg_tag = svg_tag.replace(">", f' class="{classes}">')

            # Replace the original SVG tag with the modified one
            svg_content = svg_content.replace(svg_tag, new_svg_tag)

    return svg_content


def render_page(template_name, page_name, **kwargs):
    # Calculate the folder depth based on page_name
    depth = page_name.count("/")

    # Get URLs adjusted for the current page depth
    page_urls = get_urls(depth)

    # Calculate static path based on depth
    static_path = "../" * depth + "static"

    # Load the template from the environment
    template = env.get_template(BASE_TEMPLATE)

    # Load the content template and render it first
    content_template = env.get_template(template_name)

    # Add the inject_svg function to the template context
    kwargs["inject_svg"] = inject_svg

    content = content_template.render(**kwargs)

    # Render the base template with the content and other variables
    comment_open = ""
    comment_close = ""
    if kwargs.get("preload") == "none":
        comment_open = "<!--"
        comment_close = "-->"
    if kwargs.get("title") is None:
        title = page_name
    else:
        title = kwargs.get("title")
    rendered_html = template.render(
        title=f"Hassan Kamran | {title}",
        content=content,
        home=page_urls.get("home"),
        blog=page_urls.get("blog"),
        about=page_urls.get("about"),
        sitemap=page_urls.get("sitemap"),
        preload=kwargs.get("preload"),
        comment_open=comment_open,
        comment_close=comment_close,
        static=kwargs.get(
            "static", static_path
        ),  # Use calculated static path if not provided
        inject_svg=inject_svg,
    )

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(f"./{page_name}.html"), exist_ok=True)

    with open(f"./{page_name}.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)


def home():
    render_page(
        "home.html", "index", preload="hero", title="AI Engineer & Tech Consultant"
    )


def about_me():
    render_page("about.html", "about", preload="cta")


def blog():
    blog_posts = []
    for filename in os.listdir(BLOG_FOLDER):
        if filename.endswith(".txt"):
            filepath = os.path.join(BLOG_FOLDER, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read().strip()

                # Parse metadata from the file (assuming first lines contain metadata)
                lines = content.split("\n")
                title = lines[0].strip()
                category = lines[1].strip() if len(lines) > 1 else "Uncategorized"
                date = lines[2].strip() if len(lines) > 2 else "Unknown date"
                img_name = lines[3].strip() if len(lines) > 3 else ""

                # Extract content (now as markdown)
                markdown_content = "\n".join(lines[4:]) if len(lines) > 3 else ""

                # Convert Markdown to HTML
                html_content = markdown.markdown(
                    markdown_content, extensions=["extra", "codehilite"]
                )

                filename = os.path.splitext(filename)[0]

                # Create blog post entry with correct relative path from blog list
                blog_posts.append(
                    {
                        "title": title,
                        "category": category,
                        "date": date,
                        "filename": f"./blogs/{filename}.html",
                        "image_url": f"./static/{img_name}",
                        "content": html_content,  # This is now HTML converted from Markdown
                    }
                )

                # Render the individual blog post page
                render_page(
                    "blog_post.html",
                    f"blogs/{filename}",
                    title=title,
                    category=category,
                    date=date,
                    blog_content=html_content,  # Pass the HTML content
                    preload="none",
                )
    # Render the blog list page
    render_page("blog.html", "blog", blog_posts=blog_posts, preload="none")


def sitemap():
    domain = "https://engrhassankamran.com"
    pages = []

    # Root URLs for sitemap
    root_urls = get_urls(0)

    for page_name, url in root_urls.items():
        if url.endswith(".html"):
            # Convert relative URL to absolute
            absolute_url = f"{domain}/{url.lstrip('./')}"
            pages.append(
                {
                    "loc": absolute_url,
                    "lastmod": datetime.now().strftime("%Y-%m-%d"),
                    "priority": "1.0" if page_name == "home" else "0.8",
                }
            )

    if os.path.exists("./blogs"):
        for filename in os.listdir("./blogs"):
            if filename.endswith(".html"):
                # Convert relative blog URL to absolute
                absolute_url = f"{domain}/blogs/{filename}"
                pages.append(
                    {
                        "loc": absolute_url,
                        "lastmod": datetime.now().strftime("%Y-%m-%d"),
                        "priority": "0.7",
                    }
                )

    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_content += "  <url>\n"
        sitemap_content += f"    <loc>{page['loc']}</loc>\n"
        sitemap_content += f"    <lastmod>{page['lastmod']}</lastmod>\n"
        sitemap_content += f"    <priority>{page['priority']}</priority>\n"
        sitemap_content += "  </url>\n"

    sitemap_content += "</urlset>"

    # Write sitemap.xml file
    with open("./sitemap.xml", "w", encoding="utf-8") as file:
        file.write(sitemap_content)


def robots_txt():
    domain = "https://engrhassankamran.com"

    robots_content = "# robots.txt for engrhassankamran.com\n"
    robots_content += "User-agent: *\n"
    robots_content += "Allow: /\n\n"

    # Specify the sitemap location for search engines
    robots_content += f"Sitemap: {domain}/sitemap.xml\n"

    # Write robots.txt file
    with open("./robots.txt", "w", encoding="utf-8") as file:
        file.write(robots_content)


def main():
    shutil.rmtree("./blogs")
    os.mkdir("./blogs")
    home()
    about_me()
    blog()
    sitemap()
    robots_txt()
    generate_search_index(
        output_dir=".", output_file=SEARCH_INDEX_FILE, blog_folder=BLOG_FOLDER
    )


if __name__ == "__main__":
    main()
