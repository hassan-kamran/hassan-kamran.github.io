"""Simple Static Site Generator"""

from .config import Config
from .generator import SiteGenerator

__all__ = ["Config", "SiteGenerator"]


def generate_site(config_dict=None):
    """Convenience function to generate site"""
    config = Config(**config_dict) if config_dict else Config()
    generator = SiteGenerator(config)
    generator.generate()
    return generator
