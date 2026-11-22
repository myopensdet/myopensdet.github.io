"""Make a share image (1200 x 630 PNG) for every page of the built site.

When someone posts a link on LinkedIn, X or WhatsApp, the app shows this image.
Each one shows the page title, its section, its level and the site name.

Run it after `zensical build`. It writes into site/ only, so nothing is
committed and the repository stays small however many pages there are:

    .venv/bin/zensical build
    .venv/bin/python scripts/build_share_images.py

Images are cached in .cache/share-images/ (ignored by git): a page whose title,
section and level did not change is copied from the cache, not drawn again.

The page's <meta property="og:image"> tag points to the same file
(overrides/main.html), and scripts/check_links.py checks that it exists.
Zensical cannot make share images yet; when it can, this script can go.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import build_nav  # noqa: E402  (same folder; reads page front matter)

DOCS = Path("docs")
SITE = Path("site")
OUT = SITE / "assets" / "images" / "social"
CACHE = Path(".cache/share-images")
FONTS = DOCS / "assets" / "fonts"
BOLD = FONTS / "atkinson-hyperlegible-next-latin-700-normal.woff2"
REGULAR = FONTS / "atkinson-hyperlegible-next-latin-400-normal.woff2"
VERSION = "1"  # change to redraw every image after a design change

WIDTH, HEIGHT = 1200, 630
MARGIN = 80
TOP, BOTTOM = (20, 63, 128), (31, 95, 191)  # the site's blue
WHITE = (255, 255, 255)
SOFT = (214, 228, 248)
SITE_NAME = "myOpenSDET"
SITE_ADDRESS = "myopensdet.github.io"
ROOT_LABEL = "Free SDET course"  # top label for pages outside a section


def image_name(page: Path) -> str:
    """Same name overrides/main.html uses: the page address without the last '/'."""
    rel = page.relative_to(DOCS).as_posix()
    address = rel.removesuffix("index.md") if rel.endswith("index.md") else rel[:-3] + "/"
    return (address.rstrip("/") or "index") + ".png"


def pages() -> list[Path]:
    """Every published page (docs/assets holds working files, not pages)."""
    return sorted(p for p in DOCS.rglob("*.md") if not p.is_relative_to(DOCS / "assets"))


def section_names() -> dict[str, str]:
    """Section folder -> its menu name, e.g. 'core-automation' -> 'Core Automation'."""
    names = {}
    for folder in DOCS.iterdir():
        index = folder / "index.md"
        if folder.is_dir() and index.exists():
            meta = build_nav.read_meta(index)
            if meta.get("nav_title"):
                names[folder.name] = str(meta["nav_title"])
    return names


def card_text(page: Path, sections: dict[str, str]) -> tuple[str, str, str, str]:
    meta = build_nav.read_meta(page)
    title = str(meta.get("title") or meta.get("nav_title") or SITE_NAME)
    parts = page.relative_to(DOCS).parts
    folder = parts[0] if len(parts) > 1 else str(meta.get("nav_section", ""))
    section = sections.get(folder, ROOT_LABEL)
    if page.name == "index.md" and len(parts) == 2:
        section = ROOT_LABEL  # a section overview: its title already is the section
    level = str(meta.get("level", ""))
    description = str(meta.get("description", ""))
    return title, section, level, description


def wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def background() -> Image.Image:
    """The site's blue, a soft diagonal fade, and a faint grid."""
    down = Image.linear_gradient("L").resize((WIDTH, HEIGHT))
    across = Image.linear_gradient("L").rotate(90).resize((WIDTH, HEIGHT))
    mask = Image.blend(down, across.transpose(Image.Transpose.FLIP_LEFT_RIGHT), 0.5)
    image = Image.composite(
        Image.new("RGB", (WIDTH, HEIGHT), BOTTOM), Image.new("RGB", (WIDTH, HEIGHT), TOP), mask
    )
    grid = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    lines = ImageDraw.Draw(grid)
    for x in range(0, WIDTH, 40):
        lines.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 14))
    for y in range(0, HEIGHT, 40):
        lines.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 14))
    return Image.alpha_composite(image.convert("RGBA"), grid).convert("RGB")


def draw_card(title: str, section: str, level: str, description: str) -> Image.Image:
    image = background()
    draw = ImageDraw.Draw(image)
    label_font = ImageFont.truetype(str(BOLD), 30)
    small_font = ImageFont.truetype(str(REGULAR), 26)
    name_font = ImageFont.truetype(str(BOLD), 34)

    # Section name at the top, with a short accent bar.
    draw.rounded_rectangle([MARGIN, MARGIN + 6, MARGIN + 44, MARGIN + 14], 4, fill=SOFT)
    draw.text((MARGIN + 60, MARGIN - 6), section, font=label_font, fill=SOFT)

    # The title: as large as fits in at most four lines.
    width = WIDTH - 2 * MARGIN
    for size in (68, 62, 56, 50, 46, 42):
        font = ImageFont.truetype(str(BOLD), size)
        lines = wrap(draw, title, font, width)
        if len(lines) <= 4:
            break
    lines = lines[:4]
    line_height = int(size * 1.18)
    y = MARGIN + 80
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=WHITE)
        y += line_height

    # Short titles leave room: add the page description, up to two lines.
    if len(lines) <= 2 and description:
        body_font = ImageFont.truetype(str(REGULAR), 32)
        body = wrap(draw, description, body_font, width - 120)
        if len(body) > 2:
            body = body[:2]
            body[1] = body[1].rstrip(".,;:") + "..."
        y += 18
        for line in body:
            draw.text((MARGIN, y), line, font=body_font, fill=SOFT)
            y += 44

    # Footer: site name and address on the left, level on the right.
    footer_y = HEIGHT - MARGIN - 40
    draw.text((MARGIN, footer_y - 4), SITE_NAME, font=name_font, fill=WHITE)
    name_width = draw.textlength(SITE_NAME, font=name_font)
    draw.text((MARGIN + name_width + 24, footer_y + 2), SITE_ADDRESS, font=small_font, fill=SOFT)
    if level:
        text_width = draw.textlength(level, font=small_font)
        right = WIDTH - MARGIN
        box = [right - text_width - 40, footer_y - 4, right, footer_y + 38]
        draw.rounded_rectangle(box, radius=21, outline=SOFT, width=2)
        draw.text((box[0] + 20, footer_y + 1), level, font=small_font, fill=WHITE)
    return image


def main() -> int:
    if not (SITE / "index.html").exists():
        print("build_share_images: site/ not found. Run: .venv/bin/zensical build", file=sys.stderr)
        return 1
    sections = section_names()
    CACHE.mkdir(parents=True, exist_ok=True)
    drawn = copied = 0
    for page in pages():
        title, section, level, description = card_text(page, sections)
        text = f"{VERSION}|{title}|{section}|{level}|{description}"
        key = hashlib.sha256(text.encode()).hexdigest()[:20]
        cached = CACHE / f"{key}.png"
        if not cached.exists():
            draw_card(title, section, level, description).save(cached, optimize=True)
            drawn += 1
        else:
            copied += 1
        target = OUT / image_name(page)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cached, target)
    print(f"build_share_images: {drawn + copied} images ({drawn} drawn, {copied} from cache)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
