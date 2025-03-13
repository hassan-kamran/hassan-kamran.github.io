import os
import json
import re
import markdown
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

# Constants
TEMPLATES_FOLDER = "./templates"
BASE_TEMPLATE = "base.html"
BLOG_FOLDER = "./text"
SVG_FOLDER = "./static"
SEARCH_INDEX_FILE = "./static/search-index.json"
DOMAIN = "https://engrhassankamran.com"

# Environment setup
env = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER))

# Meta descriptions for site pages
meta_des_site = {
    "home": """Engr Hassan Kamran's official website showcasing projects, 
    research, thoughts, ideas, and expertise in AI, 
    robotics, mechatronics, and the cutting edge.""",
    "about": """Discover Hassan Kamran's journey through AI, 
    Federated Learning, and robotics. With expertise in programming, big data, 
    cloud computing, and mechatronics, Hassan combines technical depth with 
    hands-on experience in startups, military leadership, and AI research. 
    Learn more about his work and projects here.""",
    "blog": """Explore cutting-edge insights on AI, Federated Learning, 
    programming, big data, and robotics. Hassan Kamran shares expert knowledge, 
    research, and hands-on experiences in machine learning, cloud computing, and more. 
    Stay ahead with in-depth technical articles and tutorials.""",
    "resume": """Professional resume of Capt (R) Engr Hassan Kamran - Technical Project Manager,
    Software Consultant and Engineer with expertise in AI, IoT, and cloud solutions. View experience, 
    qualifications, and download PDF version.""",
}

# ---- Search Index Generation Functions ----


def extract_text_from_html(html_content):
    """Extract readable text content from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Get text
    text = soup.get_text(separator=" ", strip=True)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_metadata_from_html(html_content, url):
    """Extract title and description from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract title
    title_tag = soup.find("title")
    title = title_tag.get_text() if title_tag else os.path.basename(url)

    # Extract meta description if available
    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc.get("content")

    # Try to find main heading if no description
    if not description:
        h1 = soup.find("h1")
        if h1:
            description = h1.get_text()

    return title, description


def scan_html_files(directory, base_url="", exclude_dirs=None):
    """Recursively scan directory for HTML files.

    Args:
        directory: Root directory to scan
        base_url: Base URL to prepend to relative paths
        exclude_dirs: List of directory names to exclude from scanning
    """
    if exclude_dirs is None:
        exclude_dirs = ["templates"]  # Default directories to exclude

    html_files = []

    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from the dirs list to prevent os.walk from traversing them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory)

                # Convert to URL format
                url = base_url + rel_path.replace("\\", "/")

                html_files.append({"path": file_path, "url": url})

    return html_files


def determsine_content_type(url):
    """Determsine the content type based on URL pattern."""
    if url.startswith("blogs/") or "/blogs/" in url:
        return "blog"
    elif url == "index.html":
        return "home"
    elif url == "about.html":
        return "about"
    elif url == "blog.html":
        return "blog-list"
    else:
        return "page"


def generate_search_index(
    output_dir=".", output_file="./static/search-index.json", blog_folder=None
):
    print("Generating search index...")

    # Initialize the documents list for the search index
    documents = []

    # Optional: Load blog metadata if blog_folder is provided
    blog_metadata = {}
    if blog_folder and os.path.exists(blog_folder):
        print(f"Loading blog metadata from {blog_folder}...")
        for filename in os.listdir(blog_folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(blog_folder, filename)

                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read().strip()

                    # Parse metadata from the file
                    lines = content.split("\n")
                    title = lines[0].strip()
                    category = lines[1].strip() if len(lines) > 1 else "Uncategorized"
                    date = lines[2].strip() if len(lines) > 2 else "Unknown date"

                    # Create a unique ID for the blog post
                    post_id = os.path.splitext(filename)[0]

                    # Store metadata
                    blog_metadata[post_id] = {
                        "title": title,
                        "category": category,
                        "date": date,
                    }

    # Scan for all HTML files, excluding templates and any other specified directories
    exclude_dirs = ["templates", "node_modules", ".git", ".github"]
    html_files = scan_html_files(output_dir, exclude_dirs=exclude_dirs)
    print(f"Found {len(html_files)} HTML files")

    # Process each HTML file
    for html_file in html_files:
        file_path = html_file["path"]
        url = html_file["url"]

        print(f"Processing {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

                # Extract text content
                text_content = extract_text_from_html(html_content)

                # Extract title and description
                title, description = extract_metadata_from_html(html_content, url)

                # Determsine content type
                content_type = determsine_content_type(url)

                # Create unique ID
                doc_id = os.path.splitext(url)[0].replace("/", "-")
                if doc_id == "index":
                    doc_id = "home"

                # Create document object
                document = {
                    "id": doc_id,
                    "url": url,
                    "title": title,
                    "content": text_content,
                    "description": description,
                    "type": content_type,
                }

                # Add blog-specific metadata if available
                if content_type == "blog":
                    blog_id = os.path.splitext(os.path.basename(url))[0]
                    if blog_id in blog_metadata:
                        meta = blog_metadata[blog_id]
                        document["category"] = meta.get("category", "")
                        document["date"] = meta.get("date", "")

                # Add to documents list
                documents.append(document)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Save the index as JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(documents, f)

    print(f"Search index saved to {output_file}")
    print(f"Indexed {len(documents)} documents")

    return documents


# ---- Website Generation Functions ----


def get_urls(depth=0):
    prefix = "../" * depth
    return {
        "home": f"{prefix}index.html",
        "blog": f"{prefix}blog.html",
        "about": f"{prefix}about.html",
        "sitemap": f"{prefix}sitemap.xml",
        "terms": f"{prefix}terms.html",
        "privacy": f"{prefix}privacy.html",
        "resume": f"{prefix}resume.html",
    }


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

    if kwargs.get("meta_des") is None:
        kwargs["meta_des"] = meta_des_site.get("home")

    base_url = "https://engrhassankamran.com"
    if page_name == "index":
        canonical_url = f"{base_url}/"
    else:
        canonical_url = f"{base_url}/{page_name}.html"

    kwargs["canonical"] = f'<link rel="canonical" href="{canonical_url}" />'

    template_params = {
        "title": f"Hassan Kamran | {title}",
        "content": content,
        "home": page_urls.get("home"),
        "blog": page_urls.get("blog"),
        "about": page_urls.get("about"),
        "sitemap": page_urls.get("sitemap"),
        "privacy": page_urls.get("privacy"),
        "terms": page_urls.get("terms"),
        "preload": kwargs.get("preload"),
        "comment_open": comment_open,
        "comment_close": comment_close,
        "meta_des": kwargs.get("meta_des"),
        "static": kwargs.get("static", static_path),
        "inject_svg": inject_svg,
        "resume": "hassan_resume.pdf",
        "copyright": datetime.now().year,
    }

    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in template_params}
    template_params.update(filtered_kwargs)
    rendered_html = template.render(**template_params)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(f"./{page_name}.html"), exist_ok=True)

    with open(f"./{page_name}.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)


def home():
    founder_start = datetime.strptime("2025-02", "%Y-%m")
    founder_end = datetime.today()
    years, months = divmod(
        (founder_end.year - founder_start.year) * 12
        + founder_end.month
        - founder_start.month,
        12,
    )
    duration = f"{years} yr {months} mo"

    render_page(
        "home.html",
        "index",
        preload="hero",
        title="AI Engineer & Tech Consultant",
        founder_time=duration,
    )


def privacy():
    render_page("privacy.html", "privacy", title="Privacy Policy")


def terms():
    render_page("terms.html", "terms", title="terms of service")


def resume():
    render_page(
        "resume.html",
        "resume",
        title="Capt(R) Hassan Kamran, MSc",
        download=f"{DOMAIN}/static/hassan_kamran.pdf",
        hero="hero-mini.avif",
        meta_des=meta_des_site.get("resume"),
    )


def about_me():
    render_page(
        "about.html", "about", preload="cta", meta_des=meta_des_site.get("about")
    )


def not_found_404():
    render_page("404.html", "404")


def blog():
    blog_posts = []
    for filename in os.listdir(BLOG_FOLDER):
        if filename.endswith(".md"):
            filepath = os.path.join(BLOG_FOLDER, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read().strip()

                # Parse metadata from the file (assuming first lines contain metadata)
                lines = content.split("\n")
                title = lines[0].strip()
                category = lines[1].strip() if len(lines) > 1 else "Uncategorized"
                date = lines[2].strip() if len(lines) > 2 else "Unknown date"
                img_name = lines[3].strip() if len(lines) > 3 else ""
                meta_des = lines[4].strip() if len(lines) > 3 else ""

                # Extract content (now as markdown)
                markdown_content = "\n".join(lines[5:]) if len(lines) > 3 else ""

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
                        "meta_des": meta_des,
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
                    blog_content=html_content,
                    preload="none",
                    meta_des=meta_des,
                )
    # Render the blog list page
    render_page(
        "blog.html",
        "blog",
        blog_posts=blog_posts,
        preload="none",
        meta_des=meta_des_site.get("blog"),
    )


def sitemap():
    pages = []

    # Root URLs for sitemap
    root_urls = get_urls(0)

    for page_name, url in root_urls.items():
        if url.endswith(".html"):
            # Convert relative URL to absolute
            absolute_url = f"{DOMAIN}/{url.lstrip('./')}"
            pages.append(
                {
                    "loc": absolute_url,
                    "lastmod": datetime.now().strftime("%Y-%m-%d"),
                    "priority": "1.0" if page_name == "home" else "0.8",
                }
            )

    resume_url = f"{DOMAIN}/static/hassan_resume.pdf"
    pages.append(
        {
            "loc": resume_url,
            "lastmod": datetime.now().strftime("%Y-%m-%d"),
            "priority": "0.6",
        }
    )

    if os.path.exists("./blogs"):
        for filename in os.listdir("./blogs"):
            if filename.endswith(".html"):
                # Convert relative blog URL to absolute
                absolute_url = f"{DOMAIN}/blogs/{filename}"
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
    robots_content = "# robots.txt for engrhassankamran.com\n"
    robots_content += "User-agent: *\n"
    robots_content += "Allow: /\n\n"

    # Specify the sitemap location for search engines
    robots_content += f"Sitemap: {DOMAIN}/sitemap.xml\n"

    # Write robots.txt file
    with open("./robots.txt", "w", encoding="utf-8") as file:
        file.write(robots_content)


def main():
    # Create blogs directory if it doesn't exist, or clear it if it does
    if os.path.exists("./blogs"):
        shutil.rmtree("./blogs")
    os.mkdir("./blogs")

    # Generate website pages
    home()
    about_me()
    blog()
    not_found_404()
    privacy()
    terms()
    resume()
    sitemap()
    robots_txt()

    # Generate search index
    generate_search_index(
        output_dir=".", output_file=SEARCH_INDEX_FILE, blog_folder=BLOG_FOLDER
    )

    print("Website generation complete!")


if __name__ == "__main__":
    main()
