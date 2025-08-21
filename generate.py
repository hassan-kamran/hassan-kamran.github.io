#!/usr/bin/env python3
"""
Static Site Generator for Hassan Kamran's Website
Generates website from templates and content files
"""

import os
import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from xml.etree.ElementTree import Element, SubElement, ElementTree
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# Import minification libraries (optional)
try:
    import minify_html
    import rcssmin
    import jsmin
    MINIFY_AVAILABLE = True
except ImportError:
    MINIFY_AVAILABLE = False
    print("⚠️ Minification libraries not available. Install with: uv add minify-html rcssmin jsmin")

# Configure markdown extensions
md = markdown.Markdown(extensions=['meta', 'fenced_code', 'tables', 'toc', 'attr_list', 'codehilite'])


class SiteGenerator:
    """Static site generator for personal website"""
    
    def __init__(self, config_file="site_config.yaml"):
        """Initialize the generator with configuration"""
        # Load configuration
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            # Default configuration if YAML doesn't exist
            self.config = self._get_default_config()
            
        self.domain = self.config.get('domain', 'https://engrhassankamran.com')
        self.output_dir = 'build'  # All output goes to build directory
        self.static_dir = self.config.get('assets', {}).get('static_dir', 'static')
        self.templates_dir = 'templates'
        
        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom functions
        self.env.globals['inject_svg'] = self._inject_svg
        
        # Storage for content
        self.blog_posts = []
        self.services = []
        self.gallery_images = []
        self.pages = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'domain': 'https://engrhassankamran.com',
            'title': 'Hassan Kamran - AI Engineer & Software Developer',
            'assets': {
                'output_dir': '.',
                'static_dir': 'static'
            },
            'content': {
                'blog': {
                    'source_dir': 'content/blogs',
                    'posts_per_page': 9
                },
                'services': {
                    'source_dir': 'content/services'
                },
                'gallery': {
                    'source_dir': 'content/gallery',
                    'images_per_page': 12
                }
            }
        }
        
    def generate(self):
        """Generate the entire website"""
        print("Starting website generation...")
        
        # Clean output directories
        self._clean_output()
        
        # Copy static assets
        self._copy_assets()
        
        # Load content
        self._load_blog_posts()
        self._load_services()
        self._load_gallery()
        
        print(f"Loaded {len(self.blog_posts)} blog posts")
        print(f"Loaded {len(self.services)} services")
        print(f"Loaded {len(self.gallery_images)} gallery images")
        
        # Generate pages
        self._generate_static_pages()
        self._generate_blog_pages()
        self._generate_service_pages()
        self._generate_gallery_pages()
        
        # Generate feeds and sitemaps
        self._generate_rss_feed()
        self._generate_sitemap()
        self._generate_image_sitemap()
        self._generate_robots()
        
        # Generate search index
        self._generate_search_index()
        
        # Create redirects
        self._create_redirects()
        
        # Optimize output (minification, auto-linking, etc.)
        self._optimize_output()
        
        print(f"Website generation complete! Generated {len(self.pages)} pages.")
        
    def _clean_output(self):
        """Clean and recreate output directory"""
        # Clean entire build directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        
        # Create build directory structure
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'blogs'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'services'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'static'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'gallery'), exist_ok=True)
        
    def _copy_assets(self):
        """Copy static assets to build directory"""
        print("Copying static assets...")
        
        dest_static = os.path.join(self.output_dir, 'static')
        
        # Copy all static files except SVGs (which are injected)
        for item in os.listdir(self.static_dir):
            src = os.path.join(self.static_dir, item)
            dest = os.path.join(dest_static, item)
            
            if os.path.isfile(src) and not item.endswith('.svg'):
                shutil.copy2(src, dest)
            elif os.path.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
        
        # Copy favicon files to build root
        for favicon in ['favicon.ico', 'favicon.png']:
            src = Path(favicon)
            if src.exists():
                shutil.copy2(src, os.path.join(self.output_dir, favicon))
            else:
                src = Path(self.static_dir) / favicon
                if src.exists():
                    shutil.copy2(src, os.path.join(self.output_dir, favicon))
        
        # Copy gallery images
        gallery_dir = Path('content/gallery')
        if gallery_dir.exists():
            dest_gallery = os.path.join(self.output_dir, 'gallery')
            for img_file in gallery_dir.glob('*.avif'):
                shutil.copy2(img_file, os.path.join(dest_gallery, img_file.name))
            for img_file in gallery_dir.glob('*.jpg'):
                shutil.copy2(img_file, os.path.join(dest_gallery, img_file.name))
            # Copy metadata
            metadata_file = gallery_dir / 'metadata.json'
            if metadata_file.exists():
                shutil.copy2(metadata_file, os.path.join(dest_gallery, 'metadata.json'))
        
        print("✅ Static assets copied")
        
    def _inject_svg(self, filename: str, wrap: bool = False, css_class: str = "", width: str = "", height: str = "") -> str:
        """Inject SVG content directly into HTML"""
        svg_path = Path(self.static_dir) / f"{filename}.svg"
        
        if not svg_path.exists():
            return f"<!-- SVG {filename} not found -->"
            
        try:
            svg_content = svg_path.read_text(encoding='utf-8')
            
            # Add class if specified
            if css_class:
                if 'class=' in svg_content:
                    svg_content = svg_content.replace('class="', f'class="{css_class} ', 1)
                else:
                    svg_content = svg_content.replace('<svg', f'<svg class="{css_class}"', 1)
            
            # Add width and height if specified
            if width:
                if 'width=' in svg_content:
                    import re
                    svg_content = re.sub(r'width="[^"]*"', f'width="{width}"', svg_content, count=1)
                else:
                    svg_content = svg_content.replace('<svg', f'<svg width="{width}"', 1)
                    
            if height:
                if 'height=' in svg_content:
                    import re
                    svg_content = re.sub(r'height="[^"]*"', f'height="{height}"', svg_content, count=1)
                else:
                    svg_content = svg_content.replace('<svg', f'<svg height="{height}"', 1)
                
            if wrap:
                return f'<span class="svg-wrapper">{svg_content}</span>'
            return svg_content
        except Exception as e:
            print(f"Error injecting SVG {filename}: {e}")
            return f"<!-- Error loading SVG {filename} -->"
            
    def _get_base_context(self, current_page: str = '') -> Dict[str, Any]:
        """Get base context for templates"""
        return {
            'domain': self.domain,
            'static': '/static',
            'home': '/',
            'blog': '/blog.html',
            'about': '/about.html',
            'resume': '/resume.html',
            'services_page': '/services.html',
            'gallery_page': '/gallery.html',
            'contact': '/contact.html',
            'privacy': '/privacy.html',
            'terms': '/terms.html',
            'current_page': current_page,
            'year': datetime.now().year,
            'inject_svg': self._inject_svg,
            'gallery_url': '/gallery',
        }
        
    def _load_blog_posts(self):
        """Load blog posts from markdown files"""
        blog_dir = Path(self.config.get('content', {}).get('blog', {}).get('source_dir', 'content/blogs'))
        
        if not blog_dir.exists():
            print(f"Blog directory not found: {blog_dir}")
            return
            
        self.blog_posts = []
        
        for file_path in sorted(blog_dir.glob('*.md'), reverse=True):
            try:
                content = file_path.read_text(encoding='utf-8')
                if not content.strip():
                    continue
                    
                # Parse custom format (first 5 lines are metadata)
                lines = content.split('\n')
                if len(lines) >= 5:
                    title = lines[0].strip()
                    category = lines[1].strip()
                    date = lines[2].strip()
                    image = lines[3].strip()
                    description = lines[4].strip()
                    
                    # Content starts after the metadata
                    blog_content = '\n'.join(lines[5:])
                else:
                    # Fallback to filename-based title if format is different
                    title = file_path.stem.replace('-', ' ').title()
                    category = 'General'
                    date = ''
                    image = 'default.avif'
                    description = ''
                    blog_content = content
                
                # Process content to fix image paths and template tags
                # Fix image paths - add leading slash if missing
                import re
                blog_content = re.sub(r'!\[([^\]]*)\]\(static/', r'![\1](/static/', blog_content)
                
                # Replace CTA template with actual HTML
                cta_html = '''
<section class="cta-section">
  <div class="cta-container">
    <div class="cta-wrapper">
      <h2 class="cta-title">Ready to Build Something Amazing?</h2>
      <p class="cta-description">
        Let's transform your ideas into reality with cutting-edge technology and proven expertise.
      </p>
      <a href="/contact.html" class="cta-button">
        Start Your Project
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      </a>
    </div>
  </div>
</section>
'''
                blog_content = blog_content.replace('{{template:cta}}', cta_html)
                
                # Replace video embeds with YouTube iframe
                video_pattern = r'{{video:([a-zA-Z0-9_-]+)}}'
                def replace_video(match):
                    video_id = match.group(1)
                    return f'''<div class="video-wrapper" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%;">
  <iframe 
    src="https://www.youtube.com/embed/{video_id}" 
    title="YouTube video player" 
    frameborder="0" 
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
    allowfullscreen
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
  </iframe>
</div>'''
                blog_content = re.sub(video_pattern, replace_video, blog_content)
                    
                # Parse markdown
                html = md.convert(blog_content)
                
                slug = file_path.stem.lower()
                
                self.blog_posts.append({
                    'title': title,
                    'slug': slug,
                    'date': date,
                    'category': category,
                    'image_url': f'/{image}' if image and not image.startswith('/') else image if image else '/static/default.avif',
                    'filename': f'blogs/{slug}.html',
                    'description': description,
                    'content': blog_content,
                    'content_html': html,
                    'meta_description': description or blog_content[:160] + '...',
                    'url': f'/blogs/{slug}.html'
                })
                
            except Exception as e:
                print(f"Error loading blog post {file_path}: {e}")
                
    def _load_services(self):
        """Load services from markdown files"""
        services_dir = Path(self.config.get('content', {}).get('services', {}).get('source_dir', 'content/services'))
        
        if not services_dir.exists():
            print(f"Services directory not found: {services_dir}")
            return
            
        self.services = []
        
        for file_path in sorted(services_dir.glob('*.md')):
            try:
                content = file_path.read_text(encoding='utf-8')
                if not content.strip():
                    continue
                    
                # Parse markdown
                html = md.convert(content)
                meta = md.Meta if hasattr(md, 'Meta') else {}
                
                # Extract metadata
                title = meta.get('title', [''])[0] if 'title' in meta else file_path.stem.replace('-', ' ').title()
                slug = file_path.stem.lower()
                icon = meta.get('icon', [''])[0] if 'icon' in meta else 'terminal'
                description = meta.get('description', [''])[0] if 'description' in meta else ''
                
                self.services.append({
                    'title': title,
                    'slug': slug,
                    'icon': icon,
                    'description': description,
                    'content': content,
                    'content_html': html,
                    'url': f'/services/{slug}.html'
                })
                
            except Exception as e:
                print(f"Error loading service {file_path}: {e}")
                
    def _load_gallery(self):
        """Load gallery images and metadata"""
        gallery_dir = Path(self.config.get('content', {}).get('gallery', {}).get('source_dir', 'content/gallery'))
        
        if not gallery_dir.exists():
            print(f"Gallery directory not found: {gallery_dir}")
            return
            
        self.gallery_images = []
        
        # Load metadata if exists
        metadata_file = gallery_dir / 'metadata.json'
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except Exception as e:
                print(f"Error loading gallery metadata: {e}")
                
        # Load images
        for img_path in sorted(gallery_dir.glob('*.avif')):
            img_name = img_path.stem
            img_meta = metadata.get(img_name, {})
            
            self.gallery_images.append({
                'filename': img_path.name,
                'title': img_meta.get('title', img_name.replace('-', ' ').title()),
                'description': img_meta.get('description', ''),
                'category': img_meta.get('category', 'Project'),
                'date': img_meta.get('date', ''),
                'url': f'/gallery/{img_path.name}'
            })
            
    def _generate_static_pages(self):
        """Generate static pages"""
        static_pages = [
            ('home.html', 'index.html', 'Hassan Kamran - AI Engineer & Software Developer'),
            ('about.html', 'about.html', 'About - Hassan Kamran'),
            ('resume.html', 'resume.html', 'Resume - Hassan Kamran'),
            ('contact.html', 'contact.html', 'Contact - Hassan Kamran'),
            ('privacy.html', 'privacy.html', 'Privacy Policy - Hassan Kamran'),
            ('terms.html', 'terms.html', 'Terms of Service - Hassan Kamran'),
            ('404.html', '404.html', 'Page Not Found - Hassan Kamran'),
        ]
        
        # Load base template
        base_template = self.env.get_template('base.html')
        
        for template_name, output_name, title in static_pages:
            try:
                # Load content template
                content_template = self.env.get_template(template_name)
                context = self._get_base_context(output_name.replace('.html', ''))
                context.update({
                    'title': title,
                    'meta_des': self._get_page_description(template_name),
                    'copyright': datetime.now().year,
                    'sitemap': '/sitemap.xml',
                    'image_sitemap': '/sitemap-images.xml',
                })
                
                # Add specific data for certain pages
                if template_name == 'services.html':
                    context['services'] = self.services
                if template_name == 'home.html':
                    context['custom_css'] = 'home'
                    context['preload'] = 'hero'
                    # Calculate years of experience (from 2018)
                    experience_start = 2018
                    current_year = datetime.now().year
                    context['years_experience'] = current_year - experience_start
                    # Calculate founder time
                    try:
                        from dateutil.relativedelta import relativedelta
                        start_date = datetime(2025, 2, 1)
                        now = datetime.now()
                        diff = relativedelta(now, start_date)
                        if diff.years > 0:
                            context['founder_time'] = f"{diff.years} yr {diff.months} mos" if diff.months > 0 else f"{diff.years} yr"
                        elif diff.months > 0:
                            context['founder_time'] = f"{diff.months} mos"
                        else:
                            context['founder_time'] = "Just started"
                    except:
                        context['founder_time'] = ""
                elif template_name == 'about.html':
                    context['custom_css'] = 'about'
                elif template_name == 'resume.html':
                    context['custom_css'] = 'resume'
                    context['hero'] = 'hero.avif'
                    context['download'] = '/static/hassan_resume.pdf'
                elif template_name == 'contact.html':
                    context['custom_css'] = 'contact'
                elif template_name == 'blog.html':
                    context['custom_css'] = 'blogs'
                elif template_name == 'gallery.html':
                    context['custom_css'] = 'gallery'
                elif template_name == 'privacy.html':
                    context['custom_css'] = 'info'
                elif template_name == 'terms.html':
                    context['custom_css'] = 'info'
                    
                # Render content template first
                content_html = content_template.render(**context)
                
                # Then wrap it with base template
                context['content'] = content_html
                html = base_template.render(**context)
                
                output_path = os.path.join(self.output_dir, output_name)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                    
                self.pages.append({
                    'url': f'/{output_name}' if output_name != 'index.html' else '/',
                    'title': title,
                    'output': output_name
                })
                
            except Exception as e:
                print(f"Error generating {template_name}: {e}")
                
        # Generate services listing page
        self._generate_services_page()
        
    def _generate_services_page(self):
        """Generate services listing page"""
        try:
            base_template = self.env.get_template('base.html')
            template = self.env.get_template('services.html')
            context = self._get_base_context('services')
            context.update({
                'title': 'Services - Hassan Kamran',
                'meta_des': 'Professional services offered by Hassan Kamran',
                'services': self.services,
                'custom_css': 'services',
                'copyright': datetime.now().year,
                'sitemap': '/sitemap.xml',
                'image_sitemap': '/sitemap-images.xml',
            })
            
            # Render content, then wrap with base
            content_html = template.render(**context)
            context['content'] = content_html
            html = base_template.render(**context)
            
            output_path = os.path.join(self.output_dir, 'services.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
                
        except Exception as e:
            print(f"Error generating services page: {e}")
            
    def _generate_blog_pages(self):
        """Generate blog posts and listing pages"""
        if not self.blog_posts:
            return
            
        # Generate individual blog posts
        base_template = self.env.get_template('base.html')
        template = self.env.get_template('blog_post.html')
        cta_template = self.env.get_template('cta.html')
        
        for post in self.blog_posts:
            try:
                context = self._get_base_context('blog')
                
                # Render CTA with proper context
                cta_context = self._get_base_context('blog')
                cta_html = cta_template.render(**cta_context)
                context.update({
                    'title': f"{post['title']} - Hassan Kamran",
                    'meta_des': post['meta_description'],
                    'post': post,
                    'blog_content': post['content_html'],
                    'category': post['category'],
                    'date': post['date'],
                    'cta_html': cta_html,
                    'custom_css': 'blogs',
                    'copyright': datetime.now().year,
                    'sitemap': '/sitemap.xml',
                    'image_sitemap': '/sitemap-images.xml',
                })
                
                # Render content, then wrap with base
                content_html = template.render(**context)
                context['content'] = content_html
                html = base_template.render(**context)
                output_path = os.path.join(self.output_dir, 'blogs', f"{post['slug']}.html")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                    
                self.pages.append({
                    'url': f'/blogs/{post["slug"]}.html',
                    'title': post['title'],
                    'output': output_path
                })
                
            except Exception as e:
                print(f"Error generating blog post {post['slug']}: {e}")
                
        # Generate blog listing pages with pagination
        posts_per_page = self.config.get('content', {}).get('blog', {}).get('posts_per_page', 9)
        print(f"Debug: posts_per_page = {posts_per_page}, total posts = {len(self.blog_posts)}")
        total_pages = (len(self.blog_posts) + posts_per_page - 1) // posts_per_page
        
        base_template = self.env.get_template('base.html')
        list_template = self.env.get_template('blog.html')
        
        for page_num in range(1, total_pages + 1):
            try:
                start = (page_num - 1) * posts_per_page
                end = min(start + posts_per_page, len(self.blog_posts))
                page_posts = self.blog_posts[start:end]
                print(f"Debug: Page {page_num} - showing posts {start} to {end} (total: {len(page_posts)} posts)")
                
                context = self._get_base_context('blog')
                context.update({
                    'title': f'Blog - Page {page_num} - Hassan Kamran' if page_num > 1 else 'Blog - Hassan Kamran',
                    'meta_des': 'Articles on AI, software development, and technology',
                    'blog_posts': page_posts,  # Changed from 'posts' to 'blog_posts'
                    'pagination': {
                        'current_page': page_num,
                        'total_pages': total_pages,
                        'has_prev': page_num > 1,
                        'has_next': page_num < total_pages,
                        'prev_url': 'blog.html' if page_num == 2 else f'blog-{page_num - 1}.html' if page_num > 1 else None,
                        'next_url': f'blog-{page_num + 1}.html' if page_num < total_pages else None,
                    },
                    'custom_css': 'blog',
                    'copyright': datetime.now().year,
                    'sitemap': '/sitemap.xml',
                    'image_sitemap': '/sitemap-images.xml',
                })
                
                output_name = 'blog.html' if page_num == 1 else f'blog-{page_num}.html'
                content_html = list_template.render(**context)
                context['content'] = content_html
                html = base_template.render(**context)
                
                output_path = os.path.join(self.output_dir, output_name)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                    
                self.pages.append({
                    'url': f'/{output_name}',
                    'title': context['title'],
                    'output': output_name
                })
                
            except Exception as e:
                print(f"Error generating blog listing page {page_num}: {e}")
                
    def _generate_service_pages(self):
        """Generate individual service pages"""
        if not self.services:
            return
            
        base_template = self.env.get_template('base.html')
        template = self.env.get_template('service_detail.html')
        
        # Load CTA template
        cta_template = self.env.get_template('cta.html')
        
        for service in self.services:
            try:
                context = self._get_base_context('services')
                
                # Render CTA with proper context
                cta_context = self._get_base_context('services')
                cta_html = cta_template.render(**cta_context)
                
                context.update({
                    'title': f"{service['title']} - Hassan Kamran",
                    'meta_des': service['description'],
                    'service': service,
                    'service_content': service['content_html'],
                    'cta_html': cta_html,
                    'custom_css': 'service',
                    'copyright': datetime.now().year,
                    'sitemap': '/sitemap.xml',
                    'image_sitemap': '/sitemap-images.xml',
                })
                
                # Render content, then wrap with base
                content_html = template.render(**context)
                context['content'] = content_html
                html = base_template.render(**context)
                output_path = os.path.join(self.output_dir, 'services', f"{service['slug']}.html")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                    
                self.pages.append({
                    'url': f'/services/{service["slug"]}.html',
                    'title': service['title'],
                    'output': output_path
                })
                
            except Exception as e:
                print(f"Error generating service page {service['slug']}: {e}")
                
    def _generate_gallery_pages(self):
        """Generate gallery pages with pagination"""
        images_per_page = self.config.get('content', {}).get('gallery', {}).get('images_per_page', 12)
        total_pages = max(1, (len(self.gallery_images) + images_per_page - 1) // images_per_page)
        
        base_template = self.env.get_template('base.html')
        template = self.env.get_template('gallery.html')
        
        for page_num in range(1, total_pages + 1):
            try:
                start = (page_num - 1) * images_per_page
                end = min(start + images_per_page, len(self.gallery_images))
                page_images = self.gallery_images[start:end] if self.gallery_images else []
                
                context = self._get_base_context('gallery')
                context.update({
                    'title': f'Gallery - Page {page_num} - Hassan Kamran' if page_num > 1 else 'Gallery - Hassan Kamran',
                    'meta_des': 'Portfolio and project gallery',
                    'images': page_images,
                    'page': page_num,
                    'total_pages': total_pages,
                    'has_prev': page_num > 1,
                    'has_next': page_num < total_pages,
                    'prev_page': page_num - 1,
                    'next_page': page_num + 1,
                    'custom_css': 'gallery',
                    'copyright': datetime.now().year,
                    'sitemap': '/sitemap.xml',
                    'image_sitemap': '/sitemap-images.xml',
                })
                
                output_name = 'gallery.html' if page_num == 1 else f'gallery-{page_num}.html'
                content_html = template.render(**context)
                context['content'] = content_html
                html = base_template.render(**context)
                
                output_path = os.path.join(self.output_dir, output_name)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                    
                self.pages.append({
                    'url': f'/{output_name}',
                    'title': context['title'],
                    'output': output_name
                })
                
            except Exception as e:
                print(f"Error generating gallery page {page_num}: {e}")
                
    def _generate_rss_feed(self):
        """Generate RSS feed for blog posts"""
        if not self.blog_posts:
            return
            
        # Create RSS structure
        rss = Element('rss', attrib={
            'version': '2.0',
            'xmlns:atom': 'http://www.w3.org/2005/Atom',
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/'
        })
        
        channel = SubElement(rss, 'channel')
        
        # Channel metadata
        SubElement(channel, 'title').text = 'Hassan Kamran - Blog'
        SubElement(channel, 'link').text = self.domain
        SubElement(channel, 'description').text = 'Articles on AI, software development, and technology'
        SubElement(channel, 'language').text = 'en-us'
        SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        # Self link
        atom_link = SubElement(channel, '{http://www.w3.org/2005/Atom}link')
        atom_link.set('href', f'{self.domain}/rss.xml')
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
        
        # Add blog posts (limit to 20 most recent)
        for post in self.blog_posts[:20]:
            item = SubElement(channel, 'item')
            
            SubElement(item, 'title').text = post['title']
            SubElement(item, 'link').text = f"{self.domain}{post['url']}"
            SubElement(item, 'description').text = post['description'] or post['content'][:200] + '...'
            SubElement(item, 'guid', attrib={'isPermaLink': 'true'}).text = f"{self.domain}{post['url']}"
            
            # Add date if available
            if post.get('date'):
                try:
                    date_obj = datetime.strptime(post['date'], '%Y-%m-%d')
                    SubElement(item, 'pubDate').text = date_obj.strftime('%a, %d %b %Y %H:%M:%S +0000')
                except:
                    pass
                    
            # Add content
            if post.get('content_html'):
                content_elem = SubElement(item, '{http://purl.org/rss/1.0/modules/content/}encoded')
                # Clean the HTML content to remove invalid characters
                import re
                clean_html = post['content_html']
                # Remove control characters except tab, newline, and carriage return
                clean_html = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', clean_html)
                content_elem.text = clean_html
                
        # Write to file
        tree = ElementTree(rss)
        ET.indent(tree, space='  ')
        output_path = os.path.join(self.output_dir, 'rss.xml')
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        print("✅ Generated RSS feed")
        
    def _generate_sitemap(self):
        """Generate XML sitemap"""
        urlset = Element('urlset', attrib={
            'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
        })
        
        # Add all pages
        for page in self.pages:
            url = SubElement(urlset, 'url')
            SubElement(url, 'loc').text = f"{self.domain}{page['url']}"
            SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
            
            # Set priority
            if page['url'] == '/':
                priority = '1.0'
            elif 'blog' in page['url'] or 'service' in page['url']:
                priority = '0.8'
            else:
                priority = '0.6'
                
            SubElement(url, 'priority').text = priority
            
        # Write to file
        tree = ElementTree(urlset)
        ET.indent(tree, space='  ')
        output_path = os.path.join(self.output_dir, 'sitemap.xml')
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        print("✅ Generated sitemap")
        
    def _generate_image_sitemap(self):
        """Generate comprehensive image sitemap for all images on the site"""
        urlset = Element('urlset', attrib={
            'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'xmlns:image': 'http://www.google.com/schemas/sitemap-image/1.1'
        })
        
        # Collect all images from static directory
        all_images = []
        static_dir = os.path.join(self.output_dir, 'static')
        
        # Find all image files
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.avif', '.webp')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.output_dir)
                    all_images.append({
                        'path': '/' + rel_path.replace('\\', '/'),
                        'filename': file
                    })
        
        # Group images by page
        image_pages = {}
        
        # Homepage images
        image_pages['/'] = [img for img in all_images if any(keyword in img['filename'].lower() 
                            for keyword in ['hero', 'home', 'favicon', 'logo'])]
        
        # Gallery images
        if self.gallery_images:
            image_pages['/gallery.html'] = []
            for img in self.gallery_images:
                image_pages['/gallery.html'].append({
                    'url': img['url'],
                    'title': img.get('title', ''),
                    'caption': img.get('description', '')
                })
        
        # Service page images
        image_pages['/services.html'] = [img for img in all_images if 'service' in img['filename'].lower()]
        
        # About page images
        image_pages['/about.html'] = [img for img in all_images if any(keyword in img['filename'].lower() 
                                      for keyword in ['about', 'hassan', 'profile', 'team'])]
        
        # Blog images
        image_pages['/blog.html'] = [img for img in all_images if 'blog' in img['filename'].lower()]
        
        # Add all other images to homepage
        remaining_images = [img for img in all_images if not any(
            img in page_imgs for page_imgs in image_pages.values() if isinstance(page_imgs, list)
        )]
        if remaining_images:
            if '/' not in image_pages:
                image_pages['/'] = []
            image_pages['/'].extend(remaining_images)
        
        # Generate sitemap entries
        for page_url, images in image_pages.items():
            if not images:
                continue
                
            url = SubElement(urlset, 'url')
            SubElement(url, 'loc').text = f"{self.domain}{page_url}"
            
            for img in images:
                image = SubElement(url, '{http://www.google.com/schemas/sitemap-image/1.1}image')
                
                # Handle different image data structures
                if isinstance(img, dict):
                    if 'url' in img:
                        img_loc = img['url']
                    elif 'path' in img:
                        img_loc = img['path']
                    else:
                        continue
                        
                    # Ensure URL is absolute
                    if not img_loc.startswith('http'):
                        img_loc = f"{self.domain}{img_loc}"
                    
                    SubElement(image, '{http://www.google.com/schemas/sitemap-image/1.1}loc').text = img_loc
                    
                    if img.get('title'):
                        SubElement(image, '{http://www.google.com/schemas/sitemap-image/1.1}title').text = img['title']
                    
                    if img.get('caption') or img.get('description'):
                        caption = img.get('caption') or img.get('description')
                        SubElement(image, '{http://www.google.com/schemas/sitemap-image/1.1}caption').text = caption
        
        # Write to file
        tree = ElementTree(urlset)
        ET.indent(tree, space='  ')
        output_path = os.path.join(self.output_dir, 'sitemap-images.xml')
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        print("✅ Generated comprehensive image sitemap")
        
    def _generate_robots(self):
        """Generate robots.txt"""
        robots_content = f"# robots.txt for {self.domain}\n"
        robots_content += "User-agent: *\n"
        robots_content += "Allow: /\n\n"
        robots_content += f"Sitemap: {self.domain}/sitemap.xml\n"
        
        if self.gallery_images:
            robots_content += f"Sitemap: {self.domain}/sitemap-images.xml\n"
            
        output_path = os.path.join(self.output_dir, 'robots.txt')
        with open(output_path, 'w') as f:
            f.write(robots_content)
            
        print("✅ Generated robots.txt")
        
    def _generate_search_index(self):
        """Generate search index for client-side search"""
        search_data = []
        
        # Add static pages with IDs
        static_pages_data = [
            {'id': 1, 'title': 'Home', 'url': '/', 'content': 'Hassan Kamran AI Engineer Software Developer', 'type': 'page', 'description': 'AI Engineer and Software Developer'},
            {'id': 2, 'title': 'About', 'url': '/about.html', 'content': 'About Hassan Kamran experience background', 'type': 'page', 'description': 'Learn about Hassan Kamran'},
            {'id': 3, 'title': 'Resume', 'url': '/resume.html', 'content': 'Resume CV curriculum vitae', 'type': 'page', 'description': 'Professional resume and experience'},
            {'id': 4, 'title': 'Contact', 'url': '/contact.html', 'content': 'Contact email phone reach out', 'type': 'page', 'description': 'Get in touch'},
            {'id': 5, 'title': 'Services', 'url': '/services.html', 'content': 'Services AI consulting software development training', 'type': 'page', 'description': 'Professional services offered'},
            {'id': 6, 'title': 'Gallery', 'url': '/gallery.html', 'content': 'Gallery portfolio projects work showcase', 'type': 'page', 'description': 'Project gallery and portfolio'},
            {'id': 7, 'title': 'Blog', 'url': '/blog.html', 'content': 'Blog articles posts writing technical AI machine learning', 'type': 'page', 'description': 'Technical articles and insights'},
        ]
        search_data.extend(static_pages_data)
        
        # Add blog posts
        for post in self.blog_posts:
            search_data.append({
                'id': len(search_data) + 1,
                'title': post['title'],
                'url': post['url'],
                'content': post['content'][:500],
                'description': post['description'],
                'type': 'blog',
                'date': post.get('date', '')
            })
            
        # Add services
        for service in self.services:
            search_data.append({
                'id': len(search_data) + 1,
                'title': service['title'],
                'url': service['url'],
                'content': service['content'][:500],
                'description': service['description'],
                'type': 'service'
            })
            
        # Write to JSON file in build/static
        search_index_path = os.path.join(self.output_dir, 'static', 'search-index.json')
        with open(search_index_path, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Generated search index with {len(search_data)} entries")
        
    def _create_redirects(self):
        """Create redirect pages for old URLs"""
        redirects = {
            'blogs/low-Costl-teleoperated-drone-with-integrated-sprayer-for-precision-agriculture.html': 
                '/blogs/low-Cost-teleoperated-drone-with-integrated-sprayer-for-precision-agriculture.html'
        }
        
        for old_url, new_url in redirects.items():
            redirect_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <link rel="canonical" href="{self.domain}{new_url}">
    <meta http-equiv="refresh" content="0;url={new_url}">
    <script>window.location.href = "{new_url}";</script>
</head>
<body>
    <h1>Redirecting...</h1>
    <p>This page has moved. If you are not redirected automatically, <a href="{new_url}">click here</a>.</p>
</body>
</html>"""
            
            output_path = os.path.join(self.output_dir, old_url)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(redirect_html)
                
            print(f"✅ Created redirect: {old_url} → {new_url}")
            
    def _get_page_description(self, template_name: str) -> str:
        """Get page description based on template"""
        descriptions = {
            'home.html': 'AI Engineer and Software Developer specializing in machine learning, computer vision, and full-stack development',
            'about.html': 'Learn about Hassan Kamran\'s journey in AI and software development',
            'resume.html': 'Professional resume and experience',
            'services.html': 'Professional services in AI, software development, and consulting',
            'contact.html': 'Get in touch for collaboration and opportunities',
            'privacy.html': 'Privacy policy and data protection',
            'terms.html': 'Terms of service and usage',
            '404.html': 'Page not found'
        }
        return descriptions.get(template_name, 'Hassan Kamran - AI Engineer & Software Developer')
    
    def _optimize_output(self):
        """Optimize output files (minification, auto-linking, etc.)"""
        if not MINIFY_AVAILABLE:
            print("⚠️ Skipping optimization (minification libraries not installed)")
            return
            
        print("Optimizing output...")
        
        # Process HTML files for minification and auto-linking
        html_count = 0
        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Auto-link URLs in content
                        html_content = self._auto_link_urls(html_content)
                        
                        # Minify HTML - use simpler configuration
                        try:
                            minified = minify_html.minify(html_content)
                        except:
                            # Fallback if minification fails
                            minified = html_content
                        
                        # Fix SVG viewBox attributes (convert back from viewbox to viewBox)
                        import re
                        minified = re.sub(r'viewbox=', 'viewBox=', minified, flags=re.IGNORECASE)
                        
                        # Write back the processed HTML
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(minified)
                        html_count += 1
                    except Exception as e:
                        print(f"  ⚠️ Error processing {file}: {e}")
        
        # Minify CSS files
        css_count = 0
        static_dir = os.path.join(self.output_dir, 'static')
        if os.path.exists(static_dir):
            for file in os.listdir(static_dir):
                if file.endswith('.css'):
                    file_path = os.path.join(static_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            css_content = f.read()
                        
                        minified = rcssmin.cssmin(css_content)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(minified)
                        css_count += 1
                    except Exception as e:
                        print(f"  ⚠️ Error minifying {file}: {e}")
        
        # Minify JS files
        js_count = 0
        if os.path.exists(static_dir):
            for file in os.listdir(static_dir):
                if file.endswith('.js') and not file.endswith('.min.js'):
                    file_path = os.path.join(static_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            js_content = f.read()
                        
                        minified = jsmin.jsmin(js_content)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(minified)
                        js_count += 1
                    except Exception as e:
                        print(f"  ⚠️ Error minifying {file}: {e}")
        
        print(f"✅ Processed {html_count} HTML files, minified {css_count} CSS and {js_count} JS files")
    
    def _auto_link_urls(self, html_content: str) -> str:
        """Auto-link URLs in HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all text nodes that might contain URLs
            import re
            url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
            
            for text_node in soup.find_all(string=True):
                # Skip if already in a link or script/style tag
                if text_node.parent.name in ['a', 'script', 'style', 'code', 'pre']:
                    continue
                    
                # Check if text contains URLs
                if url_pattern.search(str(text_node)):
                    # Replace URLs with links
                    new_html = url_pattern.sub(
                        lambda m: f'<a href="{m.group(0)}" target="_blank" rel="noopener">{m.group(0)}</a>',
                        str(text_node)
                    )
                    
                    # Replace the text node with new HTML
                    if new_html != str(text_node):
                        new_soup = BeautifulSoup(new_html, 'html.parser')
                        text_node.replace_with(new_soup)
            
            return str(soup)
        except Exception:
            # If auto-linking fails, return original content
            return html_content


def main():
    """Main entry point"""
    generator = SiteGenerator()
    generator.generate()


if __name__ == "__main__":
    main()