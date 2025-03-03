from jinja2 import Environment, FileSystemLoader
import os

TEMPLATES_FOLDER = "./templates"
BASE_TEMPLATE = "base.html"
BUILD_FOLDER = "."
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

    with open(f"{BUILD_FOLDER}/{page_name}.html", "w", encoding="utf-8") as file:
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
    pass


def main():
    home()
    about_me()
    blog()


if __name__ == "__main__":
    main()
