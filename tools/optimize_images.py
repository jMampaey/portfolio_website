"""Generate web-optimized WebP copies of the site's raster images and update the HTML.

Usage (from the repo root):
    python tools/optimize_images.py

What it does:
  1. For every PNG/JPG under the folders in SOURCE_DIRS, writes a resized .webp next
     to it (the original is left untouched as the full-resolution source).
     A .webp is only regenerated when it is missing or older than its source.
  2. In every HTML page, points <img> tags at the .webp version and adds
     width/height, loading="lazy" and decoding="async".
     Images that already have a loading attribute (e.g. the above-the-fold hero
     image, which uses loading="eager") keep it.

Safe to run repeatedly. Requires Pillow (pip install Pillow).
"""

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

SOURCE_DIRS = ["assets/images/projects", "assets/images/thumbnails"]

# Largest width (in px) an image is ever displayed at, times ~2 for high-DPI screens.
DEFAULT_MAX_WIDTH = 1600
MAX_WIDTH_OVERRIDES = {
    "assets/images/thumbnails/image-jesse2.png": 1000,
    "assets/images/thumbnails/image-jesse-aboutme6.png": 1400,
    "assets/images/thumbnails/project-template-image.png": 1000,
    # Full-bleed showcase image, can be shown at full viewport width.
    "assets/images/projects/whoop/asset_browser.png": 2264,
}

WEBP_QUALITY = 82

IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
SRC_ATTR = re.compile(r'\bsrc="([^"]+)"')


def convert_images():
    for source_dir in SOURCE_DIRS:
        for src in sorted((ROOT / source_dir).rglob("*")):
            if src.suffix.lower() not in (".png", ".jpg", ".jpeg"):
                continue

            dst = src.with_suffix(".webp")
            if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                continue

            rel = src.relative_to(ROOT).as_posix()
            max_width = MAX_WIDTH_OVERRIDES.get(rel, DEFAULT_MAX_WIDTH)

            Image.MAX_IMAGE_PIXELS = None  # some sources are very large photos
            with Image.open(src) as im:
                im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                if im.width > max_width:
                    height = round(im.height * max_width / im.width)
                    im = im.resize((max_width, height), Image.LANCZOS)
                im.save(dst, "WEBP", quality=WEBP_QUALITY, method=6)

            before = src.stat().st_size / 1024
            after = dst.stat().st_size / 1024
            print(f"{rel}: {before:,.0f} KB -> {after:,.0f} KB")


def set_attr(tag, name, value):
    """Add an attribute to an <img> tag unless it already has it."""
    if re.search(rf"\b{name}=", tag):
        return tag
    return re.sub(r"\s*/?>$", lambda m: f' {name}="{value}"{m.group(0)}', tag, count=1)


def update_html():
    for page in sorted(ROOT.rglob("*.html")):
        with open(page, encoding="utf-8", newline="") as f:
            html = f.read()

        def rewrite(match):
            tag = match.group(0)
            src = SRC_ATTR.search(tag).group(1)
            if not src.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                return tag  # SVG icons are already tiny

            webp_src = re.sub(r"\.(png|jpe?g)$", ".webp", src, flags=re.IGNORECASE)
            webp_path = (page.parent / webp_src).resolve()
            if not webp_path.exists():
                return tag

            tag = tag.replace(f'src="{src}"', f'src="{webp_src}"')
            with Image.open(webp_path) as im:
                tag = set_attr(tag, "width", im.width)
                tag = set_attr(tag, "height", im.height)
            tag = set_attr(tag, "loading", "lazy")
            tag = set_attr(tag, "decoding", "async")
            return tag

        updated = IMG_TAG.sub(rewrite, html)
        if updated != html:
            with open(page, "w", encoding="utf-8", newline="") as f:
                f.write(updated)
            print(f"updated {page.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    convert_images()
    update_html()
