#!/usr/bin/env python3
"""Generate PWA PNG icons from the Civic Education logo. Requires: pip install pillow"""

from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit('Install Pillow first: pip install pillow') from exc

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'frontend' / 'public'
LOGO = PUBLIC / 'civic-education-logo.png'
BRAND = (5, 150, 105)  # emerald-600 fallback


def make_icon(size: int, path: Path) -> None:
    if LOGO.is_file():
        image = Image.open(LOGO).convert('RGBA')
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        offset = ((size - image.width) // 2, (size - image.height) // 2)
        canvas.paste(image, offset, image)
        canvas = canvas.convert('RGB')
    else:
        canvas = Image.new('RGB', (size, size), BRAND)

    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, 'PNG')


if __name__ == '__main__':
    make_icon(192, PUBLIC / 'icon-192.png')
    make_icon(512, PUBLIC / 'icon-512.png')
    print(f'Wrote {PUBLIC / "icon-192.png"} and {PUBLIC / "icon-512.png"}')
