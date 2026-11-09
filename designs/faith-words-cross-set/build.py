"""Faith Words purple cross: A5 journal (transparent), cosmetic bag, and pen wrap files.
Usage: python3 designs/faith-words-cross-set/build.py <cleaned_upscaled_source.png>
"""
import sys
import numpy as np, cv2
from PIL import Image

SRC = sys.argv[1]
OUT = 'assets/products/faith-words-cross-purple'
DPI = 300
src = cv2.imread(SRC)                       # BGR, ~3312 x 2925
H, W = src.shape[:2]
CX = int(W * 0.503)                         # cross centre (x)
CY_CROSS = int(H * 0.551)                   # cross centre (y)
CY_HEART = int(H * 0.452)                   # heart / arms band (y)

def crop_resize(img, cx, cy, cw, ch, out_w, out_h):
    x0 = int(np.clip(cx - cw // 2, 0, img.shape[1] - cw)); y0 = int(np.clip(cy - ch // 2, 0, img.shape[0] - ch))
    c = img[y0:y0+ch, x0:x0+cw]
    return cv2.resize(c, (out_w, out_h), interpolation=cv2.INTER_AREA)

def save_rgb(bgr, path):
    Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).save(path, dpi=(DPI, DPI), optimize=True)

def sharpen(bgr, amount=0.9, radius=2.0):
    blur = cv2.GaussianBlur(bgr, (0, 0), radius)
    out = cv2.addWeighted(bgr, 1 + amount, blur, -amount, 0)
    # small vibrance + contrast lift so it pops on black
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.12, 0, 255); hsv[..., 2] = np.clip((hsv[..., 2] - 128) * 1.06 + 132, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def transparent(bgr, drop_zone=None):
    """DTF-ready: hard edges (no semi-transparent pixels), no specks smaller than DTF can hold."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.int32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    gold = (h >= 8) & (h <= 38) & (s > 35) & (v > 85)
    purple = (h >= 118) & (h <= 168) & (s > 55) & (v > 55)
    fg = (gold | purple).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    fg = cv2.dilate(fg, np.ones((3, 3), np.uint8))            # keep the thin dark outline edge
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)       # drop word/gold fragments too small to be real
    ok = np.zeros(n, bool); ok[1:] = st[1:, cv2.CC_STAT_AREA] >= 300
    fg = ok[lab].astype(np.uint8)
    # bright star sparkles: keep only ones big enough to survive DTF (>= ~0.6 mm)
    spark = ((v > 200) & (s < 80)).astype(np.uint8)
    spark = cv2.dilate(spark, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(spark)
    ok = np.zeros(n, bool); ok[1:] = st[1:, cv2.CC_STAT_AREA] >= 40
    spark = ok[lab].astype(np.uint8)
    mask = np.maximum(fg, spark)
    # smooth jaggies at 2x, then hard threshold -> crisp, fully opaque edges
    big = cv2.resize(mask.astype(np.float32), None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    big = cv2.GaussianBlur(big, (0, 0), 1.2)
    mask = (cv2.resize(big, (mask.shape[1], mask.shape[0]), interpolation=cv2.INTER_AREA) > 0.5).astype(np.uint8)
    # drop tiny islands and anything sitting fully inside the cleaned zone above the left arm
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        x, y, w_, h_, a = st[i]
        if a < 60: continue
        if drop_zone and x >= drop_zone[0] and y >= drop_zone[1] and x + w_ <= drop_zone[2] and y + h_ <= drop_zone[3] and a < 4000:
            continue
        keep[i] = True
    mask = keep[lab].astype(np.uint8)
    holes = 1 - mask                                          # fill pinholes inside letters
    n, lab, st, _ = cv2.connectedComponentsWithStats(holes)
    small = np.zeros(n, bool); small[1:] = st[1:, cv2.CC_STAT_AREA] < 25
    mask[small[lab]] = 1
    rgba = cv2.cvtColor(sharpen(bgr), cv2.COLOR_BGR2RGBA)
    rgba[..., 3] = mask * 255
    rgba[mask == 0, :3] = 0
    return rgba

# ---- 1. A5 journal cover, transparent (5.83 x 8.27 in) -------------------
A5W, A5H = round(5.83 * DPI), round(8.27 * DPI)               # 1749 x 2481
ch = H; cw = int(ch * A5W / A5H)
journal = crop_resize(src, CX, H // 2, cw, ch, A5W, A5H)
rgba = transparent(journal, drop_zone=(170, 840, 770, 1010))
Image.fromarray(rgba).save(f'{OUT}/faith-words-cross-A5-journal-TRANSPARENT-1749x2481.png', dpi=(DPI, DPI), optimize=True)

# ---- 2. Cosmetic bag (9 x 6.5 in) ----------------------------------------
BW, BH = round(9 * DPI), round(6.5 * DPI)                     # 2700 x 1950
cw = W; ch = int(cw * BH / BW)
bag = crop_resize(src, CX, CY_CROSS, cw, ch, BW, BH)
save_rgb(bag, f'{OUT}/faith-words-cross-cosmetic-bag-9x6.5in-2700x1950.png')

# ---- 3. Pen wrap (5 x 1.5 in) --------------------------------------------
PW, PH = round(5 * DPI), round(1.5 * DPI)                     # 1500 x 450
cw = W; ch = int(cw * PH / PW)
pen = crop_resize(src, CX, CY_HEART, cw, ch, PW, PH)
save_rgb(pen, f'{OUT}/faith-words-cross-pen-wrap-5x1.5in-1500x450.png')
print('journal', rgba.shape, 'bag', bag.shape, 'pen', pen.shape)
