"""Generate web-optimized copies of the site's videos and update the HTML.

Usage (from the repo root):
    python tools/optimize_videos.py

What it does:
  1. For every .mp4 under source-assets/videos (the full-quality originals, which
     are not deployed), writes to the same folder under assets/videos:
       <name>-web.mp4      H.264, max 1920px wide, no audio (videos are muted anyway),
                           index moved to the front so playback can start right away
       <name>-poster.webp  first frame, shown while the video loads
     Outputs are only regenerated when missing or older than their source.
  2. In every HTML page, points <video> sources at the -web.mp4 version and adds the
     poster. Videos outside the page hero no longer autoplay on load; they get
     preload="none" + data-lazy-autoplay, and js/main.js plays them when they
     scroll into view.

Safe to run repeatedly. Requires ffmpeg (winget install Gyan.FFmpeg).
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCE_ROOT = ROOT / "source-assets"
OUTPUT_ROOT = ROOT / "assets"

MAX_WIDTH = 1920
CRF = 26  # lower = better quality, bigger file
POSTER_QUALITY = 75

VIDEO_BLOCK = re.compile(r"(<video\b[^>]*>)(.*?)(</video>)", re.IGNORECASE | re.DOTALL)
SOURCE_SRC = re.compile(r'(<source\b[^>]*\bsrc=")([^"]+?)(?<!-web)\.mp4(")', re.IGNORECASE)


def find_ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return found
    # winget installs ffmpeg here, but the PATH update needs a new shell.
    packages = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    for candidate in packages.glob("Gyan.FFmpeg*/*/bin/ffmpeg.exe"):
        return str(candidate)
    raise SystemExit("ffmpeg not found. Install it with: winget install Gyan.FFmpeg")


def is_stale(output, source):
    return not output.exists() or output.stat().st_mtime < source.stat().st_mtime


def run(ffmpeg, args):
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def convert_videos(ffmpeg):
    scale = f"scale='min({MAX_WIDTH},iw)':-2"

    for src in sorted((SOURCE_ROOT / "videos").rglob("*.mp4")):
        rel = src.relative_to(SOURCE_ROOT).as_posix()
        out = OUTPUT_ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)

        web = out.with_name(f"{src.stem}-web.mp4")
        if is_stale(web, src):
            run(ffmpeg, [
                "-i", str(src),
                "-vf", scale,
                "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF),
                "-profile:v", "high", "-pix_fmt", "yuv420p",
                "-an", "-movflags", "+faststart",
                str(web),
            ])
            if web.stat().st_size >= src.stat().st_size:
                # Already efficiently encoded: keep the original video stream,
                # just drop the audio and move the index to the front.
                run(ffmpeg, ["-i", str(src), "-c:v", "copy", "-an", "-movflags", "+faststart", str(web)])

            before = src.stat().st_size / 1e6
            after = web.stat().st_size / 1e6
            print(f"{rel}: {before:,.1f} MB -> {after:,.1f} MB")

        poster = out.with_name(f"{src.stem}-poster.webp")
        if is_stale(poster, src):
            run(ffmpeg, [
                "-i", str(src), "-frames:v", "1", "-vf", scale,
                "-c:v", "libwebp", "-quality", str(POSTER_QUALITY),
                str(poster),
            ])


def add_attr(tag, attr):
    """Add an attribute to an opening tag unless it already has it."""
    name = attr.split("=")[0]
    if re.search(rf"\b{name}\b", tag):
        return tag
    return tag[:-1] + f" {attr}>"


def update_html():
    for page in sorted(ROOT.rglob("*.html")):
        with open(page, encoding="utf-8", newline="") as f:
            html = f.read()

        def rewrite(match):
            open_tag, body, close_tag = match.groups()

            source = SOURCE_SRC.search(body)
            if not source:
                return match.group(0)
            src = source.group(2)  # without .mp4

            web_path = (page.parent / f"{src}-web.mp4").resolve()
            poster_path = (page.parent / f"{src}-poster.webp").resolve()
            if not web_path.exists():
                return match.group(0)

            body = SOURCE_SRC.sub(r"\1\2-web.mp4\3", body)
            if poster_path.exists():
                open_tag = add_attr(open_tag, f'poster="{src}-poster.webp"')

            is_hero = "project-hero-video" in open_tag
            if not is_hero and re.search(r"\bautoplay\b", open_tag):
                open_tag = re.sub(r"\s+autoplay\b", "", open_tag)
                open_tag = add_attr(open_tag, 'preload="none"')
                open_tag = add_attr(open_tag, "data-lazy-autoplay")

            return open_tag + body + close_tag

        updated = VIDEO_BLOCK.sub(rewrite, html)
        if updated != html:
            with open(page, "w", encoding="utf-8", newline="") as f:
                f.write(updated)
            print(f"updated {page.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    convert_videos(find_ffmpeg())
    update_html()
