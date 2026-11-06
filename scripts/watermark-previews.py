"""Make watermarked, low-res preview images of tumbler designs.

Usage: python3 scripts/watermark-previews.py <script.ttf> <bold.ttf>
Writes assets/products/<slug>/<slug>-preview-watermarked.jpg for each design.
The clean print files are never modified.
"""
import glob, math, os, sys
from PIL import Image, ImageDraw, ImageFont

SCRIPT_FONT, BOLD_FONT = sys.argv[1], sys.argv[2]
BRAND = "Digital Dream Gal Haven"
WIDTH = 1000

def watermark(src, dst):
    im = Image.open(src).convert("RGB")
    im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    w, h = im.size

    # Tiled diagonal brand name across the whole image
    tile_font = ImageFont.truetype(SCRIPT_FONT, 46)
    diag = int(math.hypot(w, h)) + 200
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    step_x, step_y = 430, 120
    for row, y in enumerate(range(0, diag, step_y)):
        offset = (row % 2) * step_x // 2
        for x in range(-step_x, diag, step_x):
            d.text((x + offset, y), BRAND, font=tile_font, fill=(255, 255, 255, 95),
                   stroke_width=2, stroke_fill=(0, 0, 0, 55))
    layer = layer.rotate(30, resample=Image.BICUBIC)
    left, top = (diag - w) // 2, (diag - h) // 2
    layer = layer.crop((left, top, left + w, top + h))

    out = im.convert("RGBA")
    out.alpha_composite(layer)

    # Center stamp
    d = ImageDraw.Draw(out)
    big = ImageFont.truetype(SCRIPT_FONT, 92)
    small = ImageFont.truetype(BOLD_FONT, 24)
    cx, cy = w // 2, h // 2
    d.text((cx, cy - 8), BRAND, font=big, anchor="mm", fill=(255, 255, 255, 185),
           stroke_width=3, stroke_fill=(0, 0, 0, 120))
    d.text((cx, cy + 58), "PREVIEW  •  WATERMARK NOT ON PURCHASED FILE", font=small, anchor="mm",
           fill=(255, 255, 255, 200), stroke_width=2, stroke_fill=(0, 0, 0, 140))

    out.convert("RGB").save(dst, quality=82)
    return out.size

for src in sorted(glob.glob("assets/products/*/*-20oz-tumbler-2790x2460.png")):
    slug = os.path.basename(os.path.dirname(src))
    dst = os.path.join(os.path.dirname(src), f"{slug}-preview-watermarked.jpg")
    print(slug, watermark(src, dst))
