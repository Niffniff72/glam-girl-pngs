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

def transparent(bgr):
    """Keep gold/purple words, cross, heart and bright sparkles; make the black glitter transparent."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.int32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    gold = (h >= 8) & (h <= 38) & (s > 35) & (v > 85)
    purple = (h >= 118) & (h <= 168) & (s > 55) & (v > 55)
    sparkle = (v > 205) & (s < 70)
    fg = (gold | purple).astype(np.uint8)
    # close small glitter gaps inside letters and the cross, drop tiny noise specks
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fg)
    keep = np.zeros(n, bool); keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= 120
    fg = keep[lab].astype(np.uint8)
    fg = cv2.dilate(fg, np.ones((3, 3), np.uint8))           # include the dark outline edge
    mask = np.maximum(fg, sparkle.astype(np.uint8)).astype(np.float32)
    alpha = cv2.GaussianBlur(mask, (5, 5), 1.0)
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA)
    rgba[..., 3] = (alpha * 255).clip(0, 255).astype(np.uint8)
    return rgba

# ---- 1. A5 journal cover, transparent (5.83 x 8.27 in) -------------------
A5W, A5H = round(5.83 * DPI), round(8.27 * DPI)               # 1749 x 2481
ch = H; cw = int(ch * A5W / A5H)
journal = crop_resize(src, CX, H // 2, cw, ch, A5W, A5H)
rgba = transparent(journal)
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
