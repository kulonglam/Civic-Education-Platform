#!/usr/bin/env python3
"""Generate PWA PNG icons for the frontend. Requires: pip install pillow"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise SystemExit('Install Pillow first: pip install pillow') from exc

BRAND = (37, 99, 235)
WHITE = (255, 255, 255)
OUT_DIR = Path(__file__).resolve().parents[1] / 'frontend' / 'public'


def make_icon(size: int, path: Path) -> None:
    image = Image.new('RGB', (size, size), BRAND)
    draw = ImageDraw.Draw(image)
    font_size = max(size // 2, 24)
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except OSError:
        font = ImageFont.load_default()
    text = 'C'
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        ((size - text_w) / 2, (size - text_h) / 2 - size * 0.04),
        text,
        fill=WHITE,
        font=font,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, 'PNG')


if __name__ == '__main__':
    make_icon(192, OUT_DIR / 'icon-192.png')
    make_icon(512, OUT_DIR / 'icon-512.png')
    print(f'Wrote {OUT_DIR / "icon-192.png"} and {OUT_DIR / "icon-512.png"}')
