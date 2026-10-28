"""Shrinks the social cards in og/ to palette PNGs (about 3 KB per icon card, 20 KB per wide card).

Run after scripts/brand.cjs: python3 scripts/og_compress.py
"""
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parent.parent / 'og'
for f in root.rglob('*.png'):
    im = Image.open(f)
    if im.mode == 'P':
        continue
    # Icon cards are two colours plus antialiasing; wide cards also hold text, so they keep more shades.
    im.convert('RGB').quantize(colors=16 if f.parent.name == 'icon' else 64).save(f, optimize=True)
