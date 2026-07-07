#!/usr/bin/env python3
"""Build big0.dev — a single-page résumé site.

Copies the hand-authored pages, static assets, and the résumé PDF into
build/ for Cloudflare Pages. No templating, no dependencies — stdlib only.

Usage: python generate.py
"""

import logging
import shutil
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent
BUILD = ROOT / "build"

# Hand-authored pages, copied to the build root
PAGES = ["index.html", "404.html"]

# Cloudflare Pages config + SEO files, copied to the build root
ROOT_FILES = ["_redirects", "_headers", "robots.txt", "sitemap.xml"]

# Served from the build root by convention (browsers request /favicon.ico etc.)
ROOT_ASSETS = [
    "favicon.ico",
    "favicon.svg",
    "favicon.png",
    "favicon-16.png",
    "favicon-32.png",
    "favicon-48.png",
    "favicon-96.png",
    "favicon-192.png",
    "favicon-512.png",
    "apple-touch-icon.png",
    "site.webmanifest",
]

# The résumé source PDF and the URL it is served at
RESUME_SRC = ROOT / "resume" / "hassan_kamran_resume.pdf"
RESUME_OUT = "hassan-kamran-resume.pdf"


def build() -> int:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    missing: list[str] = []

    for page in PAGES:
        src = ROOT / page
        if not src.exists():
            missing.append(page)
            continue
        shutil.copy2(src, BUILD / page)

    shutil.copytree(ROOT / "static", BUILD / "static")

    for name in ROOT_ASSETS:
        src = ROOT / "static" / name
        if not src.exists():
            missing.append(f"static/{name}")
            continue
        shutil.copy2(src, BUILD / name)

    for name in ROOT_FILES:
        src = ROOT / name
        if not src.exists():
            missing.append(name)
            continue
        shutil.copy2(src, BUILD / name)

    if RESUME_SRC.exists():
        shutil.copy2(RESUME_SRC, BUILD / RESUME_OUT)
    else:
        missing.append(str(RESUME_SRC.relative_to(ROOT)))

    if missing:
        for name in missing:
            logger.error("Missing source file: %s", name)
        return 1

    n_files = sum(1 for p in BUILD.rglob("*") if p.is_file())
    logger.info("Built %d files into %s", n_files, BUILD.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(build())
