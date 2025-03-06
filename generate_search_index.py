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


def determine_content_type(url):
    """Determine the content type based on URL pattern."""
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
    """
    Generate a search index for the website content and save it as JSON.

    Args:
        output_dir: Directory containing generated HTML files
        output_file: Path where the search index JSON file will be saved
        blog_folder: Optional path to folder containing blog post text files (for metadata)
    """
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

                # Determine content type
                content_type = determine_content_type(url)

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
