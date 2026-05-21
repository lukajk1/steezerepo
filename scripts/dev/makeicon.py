"""
Takes a PNG, resizes it to 64x64, and saves it as favicon.png in the repo root.

Usage: python dev/makeicon.py <source.png>

Requires Pillow: pip install Pillow
"""

import sys
from pathlib import Path
from PIL import Image

DEV_DIR  = Path(__file__).parent
TARGET   = DEV_DIR.parent / "favicon.png"
PNG_SIZE = (64, 64)


def main():
    if len(sys.argv) < 2:
        print("Usage: python dev/makeicon.py <source.png>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.is_absolute():
        src = DEV_DIR.parent / src
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)

    img = Image.open(src).convert("RGBA")
    print(f"Source: {src.name} ({img.width}x{img.height})")

    if img.width < PNG_SIZE[0] or img.height < PNG_SIZE[1]:
        print("Warning: source is smaller than 64x64 — upscaling may look poor")

    out = img.resize(PNG_SIZE, Image.LANCZOS)
    out.save(TARGET, format="PNG")
    print(f"Exported {PNG_SIZE[0]}x{PNG_SIZE[1]} PNG -> {TARGET}")


if __name__ == "__main__":
    main()
