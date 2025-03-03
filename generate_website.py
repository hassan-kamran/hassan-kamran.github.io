from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os

TEMPLATES_FOLDER = "./templates"
BASE_TEMPLATE = "base.html"
BLOG_FOLDER = "./text"

urls = {
    "home": "./index.html",
    "blog": "./blog.html",
    "about": "./about.html",
    "sitemap": "./sitemap.xml",
}


# Create a Jinja2 environment with the template folder
env = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER))


def render_page(template_name, page_name, **kwargs):
    # Load the template from the environment
    template = env.get_template(BASE_TEMPLATE)

    # Load the content template and render it first
    content_template = env.get_template(template_name)
    content = content_template.render(**kwargs)

    # Render the base template with the content and other variables
    rendered_html = template.render(
        content=content,
        home=urls.get("home"),
        blog=urls.get("blog"),
        about=urls.get("about"),
        sitemap=urls.get("sitemap"),
        preload=kwargs.get("preload"),
        static=kwargs.get("static"),
    )

    with open(f"./{page_name}.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)


def home():
    render_page("home.html", "index", preload="hero", static="./static")


def about_me():
    render_page("about.html", "about", preload="cta", static="./static")


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
                content = "\n".join(lines[3:]) if len(lines) > 3 else ""
                filename = os.path.splitext(filename)[0]

                # Create blog post entry
                blog_posts.append(
                    {
                        "title": title,
                        "category": category,
                        "date": date,
                        "filename": f"./blogs/{filename}.html",
                        "content": content,
                    }
                )

                render_page(
                    "blog_post.html",
                    f"blogs/{filename}",
                    title=title,
                    category=category,
                    date=date,
                    blog_content=content,
                    preload="blog",
                    static="../static",
                )

    render_page(
        "blog.html", "blog", blog_posts=blog_posts, preload="blog", static="./static"
    )


def sitemap():
    domain = "https://engrhassankamran.com"
    pages = []

    for page_name, url in urls.items():
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
    home()
    about_me()
    blog()
    sitemap()
    robots_txt()


if __name__ == "__main__":
    main()
