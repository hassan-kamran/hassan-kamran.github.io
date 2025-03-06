import os
import json
import re
import markdown
from bs4 import BeautifulSoup


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


def generate_search_index(blog_folder, output_file="./static/search-index.json"):
    """
    Generate a search index for the website content and save it as JSON.

    Args:
        blog_folder: Path to the folder containing blog post text files
        output_file: Path where the search index JSON file will be saved
    """
    print("Generating search index...")

    # Initialize the documents list for the search index
    documents = []

    # Add homepage content
    documents.append(
        {
            "id": "home",
            "url": "index.html",
            "title": "Home",
            "content": "Empowering Innovation Through Collaborative Engineering",
            "type": "page",
        }
    )

    # Add about page
    documents.append(
        {
            "id": "about",
            "url": "about.html",
            "title": "About Hassan Kamran",
            "content": "Engineer based in Islamabad, striving to establish as a thought leader in science and technology",
            "type": "page",
        }
    )

    # Process blog posts
    print(f"Processing blog posts from {blog_folder}...")
    for filename in os.listdir(blog_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(blog_folder, filename)
            print(f"Processing {filepath}")

            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read().strip()

                # Parse metadata from the file
                lines = content.split("\n")
                title = lines[0].strip()
                category = lines[1].strip() if len(lines) > 1 else "Uncategorized"
                date = lines[2].strip() if len(lines) > 2 else "Unknown date"

                # Extract content (as markdown)
                markdown_content = "\n".join(lines[4:]) if len(lines) > 3 else ""

                # Convert Markdown to HTML
                html_content = markdown.markdown(
                    markdown_content, extensions=["extra", "codehilite"]
                )

                # Extract plain text for indexing
                text_content = extract_text_from_html(html_content)

                # Create a unique ID for the blog post
                post_id = os.path.splitext(filename)[0]

                # Add to documents list
                documents.append(
                    {
                        "id": post_id,
                        "url": f"blogs/{post_id}.html",
                        "title": title,
                        "category": category,
                        "date": date,
                        "content": text_content,
                        "type": "blog",
                    }
                )

    # Save the index as JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(documents, f)

    print(f"Search index saved to {output_file}")
    print(f"Indexed {len(documents)} documents")

    return documents
