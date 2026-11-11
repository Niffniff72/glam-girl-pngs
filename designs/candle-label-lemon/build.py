"""Dream Gal Haven Candles: 'Squeeze the Day' Lemon Verbena label.
Usage: python3 designs/candle-label-lemon/build.py <fonts_dir>
Outputs UV DTF PNG (3.5x2.75in, transparent outside label) + 8.5x11 sticker sheet (6 up).
"""
import os, sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONTS = sys.argv[1]
HERE = os.path.dirname(__file__)
OUT = 'assets/products/candle-squeeze-the-day'
NAME = os.environ.get('NAME', 'Squeeze the Day')
DPI = 300; LW, LH = int(3.5*DPI), int(2.75*DPI)
SCRIPT, BOLD, SEMI, MED = (f'{FONTS}/yellowtail.ttf', f'{FONTS}/montserrat-800.ttf',
                           f'{FONTS}/montserrat-700.ttf', f'{FONTS}/montserrat-500.ttf')
f = lambda p, s: ImageFont.truetype(p, s)
GOLD_D, GOLD, GOLD_L = (150, 96, 12), (226, 168, 40), (250, 214, 110)
BROWN, GREEN = (92, 52, 8), (74, 130, 52)

# ---- cut the character + slices out of the white background ---------------
src = cv2.imread(f'{HERE}/character-original.png')
h0, w0 = src.shape[:2]
white = (src.min(axis=2) > 236).astype(np.uint8)
ff = white.copy(); m = np.zeros((h0+2, w0+2), np.uint8)
for seed in [(0, 0), (w0-1, 0), (0, h0-1), (w0-1, h0-1)]:
    if ff[seed[1], seed[0]] == 1: cv2.floodFill(ff, m, seed, 2)
bg = (ff == 2).astype(np.uint8)
fg = 1 - bg
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
alpha = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 0.8)
rgba = np.dstack([cv2.cvtColor(src, cv2.COLOR_BGR2RGB), (alpha*255).astype(np.uint8)])
full = Image.fromarray(rgba, 'RGBA')
def cut(box): return full.crop(box)
girl = cut((40, 70, 990, 1420))                       # character + big lemon
slice_img = cut((720, 160, 905, 325))                # one lemon slice (top right)
spark = cut((605, 115, 675, 190))                    # one sparkle

# ---- label ------------------------------------------------------------------
lab = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
pad, R = 10, 95
shape = Image.new('L', (LW, LH), 0); ImageDraw.Draw(shape).rounded_rectangle((pad, pad, LW-pad, LH-pad), R, fill=255)
bgc = Image.new('RGBA', (LW, LH)); bd = ImageDraw.Draw(bgc)
for y in range(LH):                                   # soft cream-to-butter gradient
    t = y/LH; bd.line((0, y, LW, y), fill=(int(255-4*t), int(250-18*t), int(228-58*t), 255))
rng = np.random.default_rng(3)                        # faint polka dots
for _ in range(70):
    x, y, r = int(rng.integers(0, LW)), int(rng.integers(0, LH)), int(rng.integers(5, 11))
    bd.ellipse((x-r, y-r, x+r, y+r), fill=(250, 226, 150, 255))
lab.paste(bgc, (0, 0), shape)
d = ImageDraw.Draw(lab)
d.rounded_rectangle((pad, pad, LW-pad, LH-pad), R, outline=GOLD_D, width=14)
d.rounded_rectangle((pad+3, pad+3, LW-pad-3, LH-pad-3), R-3, outline=GOLD, width=8)
d.rounded_rectangle((pad+30, pad+30, LW-pad-30, LH-pad-30), R-28, outline=GOLD_L, width=4)

def place(img, x, y, h, rot=0, shadow=True):
    w = int(img.width * h / img.height)
    im = img.resize((w, h), Image.LANCZOS)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if shadow:
        s = Image.new('RGBA', im.size, (70, 40, 0, 0)); s.putalpha(im.getchannel('A').point(lambda v: int(v*0.35)))
        lab.alpha_composite(s.filter(ImageFilter.GaussianBlur(6)), (x+4, y+6))
    lab.alpha_composite(im, (x, y))
    return im.size

# character on the left
gh = 640; gw = int(girl.width*gh/girl.height)
place(girl, 70, (LH-gh)//2 + 10, gh)
# lemon slice corner accents (sitting on the border)
for (x, y, hh, rot) in [(LW-175, 6, 120, -18), (LW-160, LH-150, 110, 160), (20, LH-140, 105, 25), (18, 8, 95, -35)]:
    place(slice_img, x, y, hh, rot)

# text block on the right
tx = (70 + gw + LW - 60) // 2 + 5
def outlined(xy, s, font, fill, stroke, sw, anchor='mm'):
    d.text((xy[0], xy[1]+4), s, font=font, anchor=anchor, fill=(120, 80, 10, 90), stroke_width=sw, stroke_fill=(120, 80, 10, 90))
    d.text(xy, s, font=font, anchor=anchor, fill=fill, stroke_width=sw, stroke_fill=stroke)
words = NAME.split(' ', 1) if len(NAME) > 12 else [NAME]
if len(words) == 2 and NAME.lower() == 'squeeze the day':
    words = ['Squeeze', 'the Day']
y = 150 if len(words) == 2 else 210
for wd in words:
    outlined((tx, y), wd, f(SCRIPT, 100), (232, 172, 30), BROWN, 5); y += 96
y += 0
d.text((tx, y), 'LEMON VERBENA', font=f(BOLD, 42), anchor='mm', fill=GREEN)
y += 50
d.text((tx, y), 'HAND-POURED SOY CANDLE', font=f(SEMI, 23), anchor='mm', fill=BROWN)
y += 62
outlined((tx, y), 'His mercies are', f(SCRIPT, 50), GREEN, (255, 250, 230), 3)
y += 50
outlined((tx, y), 'new every morning', f(SCRIPT, 50), GREEN, (255, 250, 230), 3)
y += 50
d.text((tx, y), 'LAMENTATIONS 3:23', font=f(SEMI, 17), anchor='mm', fill=BROWN)
y += 70
outlined((tx, y), 'Dream Gal Haven Candles', f(SCRIPT, 50), GOLD, BROWN, 2)
# a few sparkles
for (x, yy, hh) in [(tx-230, 95, 34), (tx+215, 140, 26), (tx+240, 520, 22), (tx-250, 600, 20)]:
    place(spark, int(x), int(yy), hh, shadow=False)

# hard alpha for UV DTF
a = np.array(lab.getchannel('A')); a = np.where(a > 127, 255, 0).astype(np.uint8)
arr = np.array(lab); arr[..., 3] = a; arr[a == 0, :3] = 0; lab = Image.fromarray(arr)
slug = NAME.lower().replace(' ', '-')
lab.save(f'{OUT}/{slug}-lemon-verbena-candle-label-UVDTF-3.5x2.75in.png', dpi=(DPI, DPI), optimize=True)

# ---- sticker sheet, 6 up -----------------------------------------------------
PW, PH = int(8.5*DPI), int(11*DPI)
page = Image.new('RGB', (PW, PH), 'white'); pd = ImageDraw.Draw(page)
gx = gy = int(.3*DPI); x0 = (PW-(2*LW+gx))//2; y0 = (PH-(3*LH+2*gy))//2
for r in range(3):
    for c in range(2):
        px, py = x0 + c*(LW+gx), y0 + r*(LH+gy)
        page.paste(lab, (px, py), lab)
        pd.rounded_rectangle((px+pad-6, py+pad-6, px+LW-pad+6, py+LH-pad+6), R+6, outline=(185, 185, 185), width=2)
ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
pd.text((PW//2, PH-y0//2), 'Print at 100% / Actual Size on glossy sticker paper  •  Cut on the gray lines  •  6 labels, 3.5" x 2.75"', font=ft, fill=(120, 120, 120), anchor='mm')
L = 2*DPI; lx = (PW-L)//2; ly = y0//2-10
pd.line((lx, ly, lx+L, ly), fill=(120, 120, 120), width=3); pd.line((lx, ly-12, lx, ly+12), fill=(120, 120, 120), width=3); pd.line((lx+L, ly-12, lx+L, ly+12), fill=(120, 120, 120), width=3)
pd.text((PW//2, ly+14), 'size check: this line = 2 inches', font=ft, fill=(120, 120, 120), anchor='ma')
page.save(f'{OUT}/{slug}-lemon-verbena-candle-label-STICKER-SHEET-8.5x11-6up.png', dpi=(DPI, DPI), optimize=True)
print('ok')
