# Hassan Kamran's Personal Portfolio Website

## Overview

This is the source code for my personal portfolio website, showcasing my professional experience, projects, publications, and insights as a Founder, AI Engineer, and Technical Project Manager.

### 🌐 Website
- **Live Site**: [capt.pk](https://capt.pk)
- **Business Site**: [big0.dev](https://big0.dev)

## 🚀 Features

### Core Features
- **Responsive Design**: Mobile-first approach with optimized layouts for all devices
- **Static Site Generation**: Fast, secure, and SEO-friendly static site built with Python and Jinja2
- **Blog System**: Dynamic blog generation from Markdown files with categories and pagination
- **Professional Portfolio**: Showcasing experience, certifications, and achievements
- **Interactive Timeline**: JavaScript-free experience timeline using CSS animations
- **Client-Side Search**: MiniSearch integration for instant content discovery
- **Image Gallery**: Responsive gallery with zoom functionality
- **Contact Integration**: Direct links to social profiles and professional networks

### Performance & SEO
- **Optimized Assets**: Minified CSS/JS and AVIF image format for faster loading
- **Comprehensive Sitemaps**: XML sitemap and image sitemap for better indexing
- **RSS Feed**: Auto-generated RSS feed for blog subscribers
- **Meta Tags**: Open Graph and Twitter Card support
- **Clean URLs**: SEO-friendly URL structure with redirects for legacy links

### Design System
- **CSS Variables**: Consistent design tokens for colors, spacing, and typography
- **Component-Based**: Reusable components for cards, buttons, and layouts
- **Modern CSS**: Flexbox, Grid, and CSS custom properties
- **Accessibility**: ARIA labels, semantic HTML, and keyboard navigation

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, Modern JavaScript (ES6+)
- **Static Site Generation**: Python 3.13, Jinja2
- **Build Tools**: Python scripts for generation and optimization
- **Search**: MiniSearch for client-side full-text search
- **Deployment**: GitHub Pages with custom domain
- **Image Format**: AVIF for optimal compression and quality

## 📦 Project Structure

```
.
├── build/              # Generated static site output
├── content/            # Content source files
│   ├── blogs/          # Blog posts in Markdown format
│   ├── gallery/        # Gallery metadata
│   └── services/       # Service descriptions
├── static/             # Static assets
│   ├── *.css           # Stylesheets (base, components, page-specific)
│   ├── *.avif          # Optimized images
│   ├── *.svg           # Vector graphics and icons
│   └── *.js            # JavaScript files (search, timeline, etc.)
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Main layout template
│   ├── home.html       # Homepage with experience timeline
│   ├── blog.html       # Blog listing with pagination
│   ├── about.html      # About page
│   ├── resume.html     # Interactive resume
│   ├── services.html   # Services overview
│   ├── gallery.html    # Image gallery
│   └── contact.html    # Contact information
├── generate.py         # Main static site generation script
├── site_config.yaml    # Site configuration
├── pyproject.toml      # Project dependencies (uv)
└── README.md           # Project documentation
```

## 🔧 Setup and Installation

### Prerequisites

- Python 3.13+
- uv (Python package manager) or pip

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/hassan-kamran/hassan-kamran.github.io.git
   cd hassan-kamran.github.io
   ```

2. Install dependencies using uv (recommended)
   ```bash
   uv pip install -r requirements.txt
   ```
   
   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. Generate the static site
   ```bash
   python generate.py
   ```

4. Serve locally for development
   ```bash
   cd build
   python -m http.server 8000
   ```

5. Visit `http://localhost:8000` in your browser

## 🌈 Key Functionalities

### Content Management
- **Markdown Blog Posts**: Write blog posts in Markdown with YAML frontmatter
- **Automatic Pagination**: Blog posts are automatically paginated (9 per page)
- **Category System**: Organize content by categories
- **Image Optimization**: Automatic image sitemap generation

### Developer Experience
- **Hot Reload**: Local development server with Python's built-in server
- **Clean URLs**: Automatic URL generation from filenames
- **Redirect Handling**: Legacy URL redirects for SEO preservation
- **Build Optimization**: Automatic CSS/JS minification in production

### Recent Updates (2025)
- **CSS Optimization**: Consolidated design system with reduced redundancy
- **Experience Timeline**: Fixed card flickering with proper height management
- **SVG Fixes**: Improved color inheritance for logo SVGs
- **Blog Enhancements**: Added comprehensive content for technical blogs
- **Image Sitemaps**: Complete image indexing for all site images
- **PDF Button**: Improved hover state legibility on resume download

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open-source. See the LICENSE file for details.

## 📧 Contact

- **Email**: [contact@engrhassankamran.com](mailto:contact@engrhassankamran.com)
- **LinkedIn**: [Engr Hassan Kamran](https://www.linkedin.com/in/engr-hassan-kamran)
- **Website**: [engrhassankamran.com](https://engrhassankamran.com)
