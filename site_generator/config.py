from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Config:
    """Simple configuration"""

    # Paths
    gallery_dir: str = "./content/gallery"
    templates_dir: str = "./templates"
    output_dir: str = "./"
    static_dir: str = "./static"
    blog_dir: str = "./content/blogs"
    services_dir: str = "./content/services"

    # Site info
    domain: str = "https://engrhassankamran.com"
    base_title: str = "Hassan Kamran"

    # Features
    posts_per_page: int = 4
    gallery_imgs_per_page: int = 4

    # Redirects
    redirects: Dict[str, str] = field(
        default_factory=lambda: {
            "blogs/low-Costl-teleoperated-drone-with-integrated-sprayer-for-precision-agriculture.html": "/blogs/low-Cost-teleoperated-drone-with-integrated-sprayer-for-precision-agriculture.html",
        }
    )
