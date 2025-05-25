from typing import Dict, Any, List  # Add List to the import
from pathlib import Path
from datetime import datetime
from .core import Page, TemplateRenderer


class HomePage(Page):
    @property
    def slug(self) -> str:
        return "index"

    @property
    def title(self) -> str:
        return "AI Engineer & Tech Consultant"

    @property
    def custom_css(self) -> str:
        return "home"

    @property
    def template(self) -> str:
        return "home.html"

    @property
    def output_path(self) -> Path:
        return Path("index.html")

    @property
    def meta_description(self) -> str:
        return "Engr Hassan Kamran's official website showcasing projects, research, thoughts, ideas, and expertise in AI, robotics, mechatronics, and the cutting edge."

    @property
    def preload(self) -> str:
        return "hero"

    def get_context(self) -> Dict[str, Any]:
        # Calculate founder time
        start = datetime.strptime("2025-02", "%Y-%m")
        end = datetime.today()
        years, months = divmod(
            (end.year - start.year) * 12 + end.month - start.month, 12
        )

        return {"founder_time": f"{years} yr {months} mo"}


class AboutPage(Page):
    @property
    def slug(self) -> str:
        return "about"

    @property
    def title(self) -> str:
        return "About"

    @property
    def template(self) -> str:
        return "about.html"

    @property
    def output_path(self) -> Path:
        return Path("about.html")

    @property
    def meta_description(self) -> str:
        return "Discover Hassan Kamran's journey through AI, Federated Learning, and robotics. With expertise in programming, big data, cloud computing, and mechatronics."

    @property
    def preload(self) -> str:
        return "cta"

    @property
    def custom_css(self) -> str:
        return "about"


class ResumePage(Page):
    @property
    def slug(self) -> str:
        return "resume"

    @property
    def title(self) -> str:
        return "Capt(R) Hassan Kamran, MSc"

    @property
    def template(self) -> str:
        return "resume.html"

    @property
    def output_path(self) -> Path:
        return Path("resume.html")

    @property
    def meta_description(self) -> str:
        return "Professional resume of Capt (R) Engr Hassan Kamran - Technical Project Manager, Software Consultant and Engineer with expertise in AI, IoT, and cloud solutions."

    def get_context(self) -> Dict[str, Any]:
        return {
            "download": f"{self.config.domain}/static/hassan_resume.pdf",
            "hero": "hero-mini.avif",
        }

    @property
    def custom_css(self) -> str:
        return "resume"


class ContactPage(Page):
    @property
    def slug(self) -> str:
        return "contact"

    @property
    def title(self) -> str:
        return "Get in Touch"

    @property
    def template(self) -> str:
        return "contact.html"

    @property
    def output_path(self) -> Path:
        return Path("contact.html")

    @property
    def meta_description(self) -> str:
        return "Get in touch with Hassan Kamran, Software Engineer & Developer. Connect via email, phone, or social media for collaboration opportunities."

    @property
    def custom_css(self) -> str:
        return "contact"


class PrivacyPage(Page):
    @property
    def slug(self) -> str:
        return "privacy"

    @property
    def title(self) -> str:
        return "Privacy Policy"

    @property
    def template(self) -> str:
        return "privacy.html"

    @property
    def output_path(self) -> Path:
        return Path("privacy.html")

    @property
    def meta_description(self) -> str:
        return "Privacy Policy for Hassan Kamran's website. Learn how your personal information is collected, used, and protected when you visit engrhassankamran.com."

    @property
    def custom_css(self) -> str:
        return "info"


class TermsPage(Page):
    @property
    def slug(self) -> str:
        return "terms"

    @property
    def title(self) -> str:
        return "Terms of Service"

    @property
    def template(self) -> str:
        return "terms.html"

    @property
    def output_path(self) -> Path:
        return Path("terms.html")

    @property
    def meta_description(self) -> str:
        return "Terms of Service for engrhassankamran.com. Understand the rules, guidelines, and legal agreements that govern the use of Hassan Kamran's website."

    @property
    def custom_css(self) -> str:
        return "info"


class NotFoundPage(Page):
    @property
    def slug(self) -> str:
        return "404"

    @property
    def title(self) -> str:
        return "OOPs Not Found"

    @property
    def template(self) -> str:
        return "404.html"

    @property
    def output_path(self) -> Path:
        return Path("404.html")

    @property
    def meta_description(self) -> str:
        return "Page not found"

    def get_context(self) -> Dict[str, Any]:
        return {}

    @property
    def custom_css(self) -> str:
        return "about"


class ServicesPage(Page):
    """Services listing page"""

    def __init__(self, renderer: TemplateRenderer):
        super().__init__(renderer)
        self._services = []

    def set_services(self, services: List):
        """Set services data"""
        self._services = services

    @property
    def slug(self) -> str:
        return "services"

    @property
    def title(self) -> str:
        return "Services"

    @property
    def template(self) -> str:
        return "services.html"

    @property
    def output_path(self) -> Path:
        return Path("services.html")

    @property
    def meta_description(self) -> str:
        return "Professional services offered by Hassan Kamran - AI consulting, software development, technical project management, and engineering solutions."

    def get_context(self) -> Dict[str, Any]:
        return {"services": self._services}

    @property
    def custom_css(self) -> str:
        return "services"


class GalleryPage(Page):
    """Gallery page"""

    def __init__(self, renderer: TemplateRenderer):
        super().__init__(renderer)
        self._images = []

    def set_images(self, images: List):
        """Set gallery images"""
        self._images = images

    @property
    def slug(self) -> str:
        return "gallery"

    @property
    def title(self) -> str:
        return "Gallery"

    @property
    def template(self) -> str:
        return "gallery.html"

    @property
    def output_path(self) -> Path:
        return Path("gallery.html")

    @property
    def meta_description(self) -> str:
        return "Photo gallery showcasing Hassan Kamran's projects, experiences, and achievements in AI, robotics, and technology."

    def get_context(self) -> Dict[str, Any]:
        return {
            "images": self._images,
            "gallery_url": f"{self.renderer.config.gallery_dir}",
        }

    @property
    def custom_css(self) -> str:
        return "gallery"
