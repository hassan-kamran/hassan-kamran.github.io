# Hassan Kamran's Personal Portfolio Website

## Overview

This is the source code for my personal portfolio website, showcasing my professional experience, projects, publications, and insights as an AI Engineer and Technical Project Manager.

### 🌐 Website
- **Live Site**: [engrhassankamran.com](https://engrhassankamran.com)

## 🚀 Features

- Responsive design
- Blog with dynamic content generation
- Professional portfolio sections
- SEO-optimized
- Sitemap and robots.txt generation
- SVG icon management
- Modern web technologies

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3
- **Static Site Generation**: Python, Jinja2
- **Deployment**: GitHub Pages

## 📦 Project Structure

```
.
├── static/             # Static assets (SVGs, images)
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Main page layout
│   ├── home.html       # Homepage template
│   ├── blog.html       # Blog listing template
│   └── blog_post.html  # Individual blog post template
├── text/               # Blog post content files
├── generate_website.py # Static site generation script
├── pyproject.toml      # Project dependencies
└── README.md           # Project documentation
```

## 🔧 Setup and Installation

### Prerequisites

- Python 3.13+
- pip

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/hassan-kamran/hassan-kamran.github.io.git
   cd hassan-kamran.github.io
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Generate the static site
   ```bash
   python generate_website.py
   ```

## 🌈 Key Functionalities

- **Dynamic Blog Generation**: Automatically generates blog pages from markdown files
- **SVG Injection**: Custom SVG handling with color manipulation
- **Responsive Design**: Mobile-friendly layout
- **SEO Optimization**: Sitemap and robots.txt generation

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
