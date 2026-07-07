#!/usr/bin/env python3
"""Local preview server for build/ that mimics Cloudflare Pages URL handling.

The site emits extensionless URLs (/about, /blogs/foo) which Pages serves
natively from about.html etc. A plain `python -m http.server` 404s on those,
so use this instead:

    python serve.py [port]      # default port 8000
"""

import functools
import http.server
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent / "build"


class PagesHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        resolved = super().translate_path(path)
        candidate = Path(resolved)
        # /about -> about.html, like Cloudflare Pages pretty URLs. Pages
        # prefers blogs.html over the blogs/ directory for /blogs, so the
        # .html twin wins even when a same-named directory exists.
        if not candidate.suffix:
            html_fallback = candidate.with_suffix(".html")
            if html_fallback.exists():
                return str(html_fallback)
        return resolved


def main():
    if not BUILD_DIR.exists():
        sys.exit("build/ not found — run `python generate.py` first")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(PagesHandler, directory=str(BUILD_DIR))
    print(f"Serving {BUILD_DIR} at http://localhost:{port} (extensionless URLs supported)")
    http.server.ThreadingHTTPServer(("", port), handler).serve_forever()


if __name__ == "__main__":
    main()
