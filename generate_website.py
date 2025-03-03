from jinja2 import Environment, FileSystemLoader

TEMPLATES_FOLDER = "./templates"
BASE_TEMPLATE = "base.html"
BUILD_FOLDER = "."

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
    )

    with open(f"{BUILD_FOLDER}/{page_name}.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)


def home():
    render_page("home.html", "index")


def about_me():
    render_page("about.html", "about")


def main_blog():
    pass


def blog_pages():
    pass


def sitemap():
    pass


def main():
    home()
    about_me()


if __name__ == "__main__":
    main()
