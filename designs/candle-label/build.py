"""Dream Gal Haven Candles label: 'Blessed & Highly Favored', Lavender.
Outputs: UV DTF transparent PNG (3.5x2.75in) + 8.5x11 sticker sheet (6 up).
Usage: python3 designs/candle-label/build.py <fonts_dir> <cross_clean_up.png> <cross_mask.png>
"""
import sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
FONTS, SRC, MASK = sys.argv[1:4]
import os
CLEAR = os.environ.get('CLEAR') == '1'
OUT = 'assets/products/candle-blessed-highly-favored'
DPI = 300
LW, LH = int(3.5*DPI), int(2.75*DPI)          # 1050 x 825
SCRIPT, BOLD, SEMI = f'{FONTS}/yellowtail.ttf', f'{FONTS}/montserrat-800.ttf', f'{FONTS}/montserrat-700.ttf'
f = lambda p, s: ImageFont.truetype(p, s)

def gold_text(img, xy, text, font, anchor='mm', stroke=4):
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).text(xy, text, font=font, anchor=anchor, fill=255)
    ms = Image.new('L', img.size, 0); ImageDraw.Draw(ms).text(xy, text, font=font, anchor=anchor, fill=255, stroke_width=stroke, stroke_fill=255)
    x0, y0, x1, y1 = ms.getbbox()
    sh = Image.new('RGBA', img.size, (10, 0, 15, 0)); sh.putalpha(ms.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v*0.85)))
    img.alpha_composite(sh, (0, 4))
    o = Image.new('RGBA', img.size, (70, 32, 6, 255)); o.putalpha(ms); img.alpha_composite(o)
    g = Image.new('RGBA', img.size); gd = ImageDraw.Draw(g)
    stops = [(0, (255, 246, 205)), (.38, (247, 205, 96)), (.52, (196, 138, 38)), (.62, (232, 178, 70)), (1, (255, 226, 140))]
    hh = max(y1-y0, 1)
    for yy in range(y0, y1+1):
        t = (yy-y0)/hh
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= t <= b:
                k = (t-a)/(b-a); c = tuple(int(ca[i]+(cb[i]-ca[i])*k) for i in range(3)); break
        gd.line((x0, yy, x1, yy), fill=c+(255,))
    gf = Image.new('RGBA', img.size, (0, 0, 0, 0)); gf.paste(g, (0, 0), m); img.alpha_composite(gf)

# ---- source design pieces -------------------------------------------------
src = cv2.imread(SRC); H, W = src.shape[:2]; k = W/1104.0
m = cv2.imread(MASK, 0); x, y, bw, bh = cv2.boundingRect(m)
nw, nh = int(bw*1.3), int(bh*1.3)
M = np.zeros(m.shape, np.uint8)
M[y+bh//2-nh//2:y+bh//2-nh//2+nh, x+bw//2-nw//2:x+bw//2-nw//2+nw] = cv2.resize(m[y:y+bh, x:x+bw], (nw, nh))
M = (cv2.resize(M, (W, H)) > 127).astype(np.uint8)
M = cv2.dilate(M, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(5*k), int(5*k))))
cx0, cy0, cw, ch = cv2.boundingRect(M)
# ---- clean cross cut-out with a fresh, even outline ----
PADC = int(30*k)
y0c, y1c = max(cy0-PADC, 0), min(cy0+ch+PADC, H); x0c, x1c = max(cx0-PADC, 0), min(cx0+cw+PADC, W)
crop = src[y0c:y1c, x0c:x1c]; Mc = M[y0c:y1c, x0c:x1c]
hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV).astype(int)
goldc = ((hsv[..., 0] >= 8) & (hsv[..., 0] <= 38) & (hsv[..., 1] > 35) & (hsv[..., 2] > 80)).astype(np.uint8)
inner = cv2.erode(Mc, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(9*k), int(9*k))))
shape_ = (goldc & cv2.dilate(Mc, np.ones((5, 5), np.uint8))).astype(np.uint8)
shape_ = cv2.morphologyEx(shape_, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(7*k)|1, int(7*k)|1)))
n_, lb_, st_, _ = cv2.connectedComponentsWithStats(shape_)
shape_ = (lb_ == 1 + np.argmax(st_[1:, cv2.CC_STAT_AREA])).astype(np.uint8)      # keep the cross only
ff = shape_.copy(); cv2.floodFill(ff, np.zeros((ff.shape[0]+2, ff.shape[1]+2), np.uint8), (0, 0), 1)
shape_ = shape_ | (1 - ff)                                                            # fill holes
shape_ = cv2.morphologyEx(shape_, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(9*k)|1, int(9*k)|1)))   # trim bumps
n_, lb_, st_, _ = cv2.connectedComponentsWithStats(shape_)
shape_ = (lb_ == 1 + np.argmax(st_[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
Kb = int(19*k)|1
opened = cv2.morphologyEx(shape_, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (Kb, Kb)))
prot = (shape_ & (1 - opened)).astype(np.uint8)
n_, lb_, st_, cen_ = cv2.connectedComponentsWithStats(prot)
for i in range(1, n_):
    x_, y_, w_, h_, a_ = st_[i]
    # contact length with the main body: bumps touch along a short neck, corner slivers along two long edges
    comp = (lb_ == i).astype(np.uint8)
    contact = int((cv2.dilate(comp, np.ones((3, 3), np.uint8)) & opened).sum())
    if os.environ.get('DEBUG') and a_ > 40: print('prot', i, x_, y_, w_, h_, a_, 'contact', contact)
    if a_ > 40:
        shape_[comp == 1] = 0
n_, lb_, st_, _ = cv2.connectedComponentsWithStats(shape_)
shape_ = (lb_ == 1 + np.argmax(st_[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
sm = cv2.GaussianBlur(shape_.astype(np.float32), (0, 0), 2.2*k)
shape_ = (sm > 0.5).astype(np.uint8)                                                 # smooth edge
ow = int(round(4.5*k))
outline = cv2.dilate(shape_, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*ow+1, 2*ow+1)))
rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB).astype(np.float32)
out = np.zeros(crop.shape[:2] + (4,), np.float32)
out[outline == 1, :3] = (62, 28, 6)                       # dark chocolate outline (matches gold text)
out[shape_ == 1, :3] = rgb[shape_ == 1]
alpha = cv2.GaussianBlur(outline.astype(np.float32), (0, 0), 0.8)
out[..., 3] = alpha*255
cross_img = Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA')
Lp = src[:, :int(cx0-10*k)]; Rp = src[:, int(cx0+cw+10*k):]
SC = 0.36
def piece(a, top, hh):
    top = int(np.clip(top, 0, a.shape[0]-hh)); q = a[top:top+hh]
    return cv2.resize(q, (int(q.shape[1]*SC), int(hh*SC)), interpolation=cv2.INTER_AREA)
hh = int(LH/SC)+4
strip = np.concatenate([piece(Lp, 200, hh), piece(Rp, 900, hh), piece(Lp, 1400, hh)], axis=1)
pattern = Image.fromarray(cv2.cvtColor(strip, cv2.COLOR_BGR2RGB))   # smaller, sharper words

# ---- label ----------------------------------------------------------------
lab = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
pad, R = 10, 95
shape = Image.new('L', (LW, LH), 0); ImageDraw.Draw(shape).rounded_rectangle((pad, pad, LW-pad, LH-pad), R, fill=255)
# background: words pattern, darkened with deep purple so text reads clearly
bg = ImageOps.fit(pattern, (LW, LH), Image.LANCZOS, centering=(0.5, 0.5)).convert('RGBA')
bg = Image.blend(bg, Image.new('RGBA', (LW, LH), (24, 6, 34, 255)), 0.62)
if not CLEAR:
    lab.paste(bg, (0, 0), shape)
d = ImageDraw.Draw(lab)
d.rounded_rectangle((pad, pad, LW-pad, LH-pad), R, outline=(110, 66, 10), width=14)
d.rounded_rectangle((pad+3, pad+3, LW-pad-3, LH-pad-3), R-3, outline=(240, 198, 92), width=8)
d.rounded_rectangle((pad+30, pad+30, LW-pad-30, LH-pad-30), R-28, outline=(232, 182, 75), width=3)
# cross on the left
chh = 540; cww = int(cross_img.width*chh/cross_img.height)
cr = cross_img.resize((cww, chh), Image.LANCZOS)
shad = Image.new('RGBA', cr.size, (0, 0, 0, 0)); shad.putalpha(cr.getchannel('A').point(lambda v: int(v*0.7)))
lab.alpha_composite(shad.filter(ImageFilter.GaussianBlur(8)), (95, (LH-chh)//2+8))
lab.alpha_composite(cr, (90, (LH-chh)//2))
# text on the right
tx = (90 + cww + 30 + LW - 70) // 2
gold_text(lab, (tx, 220), 'Blessed &', f(SCRIPT, 100))
gold_text(lab, (tx, 335), 'Highly Favored', f(SCRIPT, 84))
d = ImageDraw.Draw(lab)
d.text((tx, 460), 'LAVENDER', font=f(BOLD, 52), anchor='mm', fill=(92, 30, 140) if CLEAR else (214, 186, 255), stroke_width=3 if CLEAR else 0, stroke_fill=(240, 198, 92))
lw_ = d.textlength('LAVENDER', font=f(BOLD, 52))
for side in (-1, 1):
    x1 = tx + side*(lw_/2 + 18); x2 = tx + side*(lw_/2 + 62)
    d.line((x1, 460, x2, 460), fill=(232, 182, 75), width=4)
d.text((tx, 532), 'HAND-POURED SOY CANDLE', font=f(SEMI, 25), anchor='mm', fill=(60, 20, 80) if CLEAR else (245, 232, 210), stroke_width=2 if CLEAR else 0, stroke_fill=(240, 220, 170))
gold_text(lab, (tx, 635), 'Dream Gal Haven Candles', f(SCRIPT, 50), stroke=3)
# soft 4-point twinkles in open corners
def twinkle(img, cx, cy, size):
    t = Image.new('RGBA', img.size, (0, 0, 0, 0)); td = ImageDraw.Draw(t)
    td.polygon([(cx, cy-size), (cx+size*0.18, cy), (cx, cy+size), (cx-size*0.18, cy)], fill=(255, 246, 220, 235))
    td.polygon([(cx-size, cy), (cx, cy-size*0.18), (cx+size, cy), (cx, cy+size*0.18)], fill=(255, 246, 220, 235))
    img.alpha_composite(t.filter(ImageFilter.GaussianBlur(0.6)))
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((cx-size*.45, cy-size*.45, cx+size*.45, cy+size*.45), fill=(255, 235, 190, 120))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(size*0.3)))
for (sx, sy, sz) in [(tx-230, 130, 16), (tx+235, 150, 12), (tx+250, 545, 10), (tx-245, 560, 10), (tx, 735, 9)]:
    twinkle(lab, int(sx), int(sy), sz)
# hard alpha for UV DTF
a = np.array(lab.getchannel('A')); a = np.where(a > 127, 255, 0).astype(np.uint8)
lab.putalpha(Image.fromarray(a)); arr = np.array(lab); arr[a == 0, :3] = 0; lab = Image.fromarray(arr)
name = 'CLEAR-UVDTF' if CLEAR else 'UVDTF'
lab.save(f'{OUT}/blessed-highly-favored-candle-label-{name}-3.5x2.75in.png', dpi=(DPI, DPI), optimize=True)

if CLEAR:
    print('clear ok'); sys.exit()
# ---- 8.5x11 sticker sheet, 6 up ------------------------------------------
PW, PH = int(8.5*DPI), int(11*DPI)
page = Image.new('RGB', (PW, PH), 'white'); pd = ImageDraw.Draw(page)
cols, rows, gx, gy = 2, 3, int(.3*DPI), int(.3*DPI)
x0 = (PW - (cols*LW + gx)) // 2; y0 = (PH - (rows*LH + 2*gy)) // 2
for r in range(rows):
    for c in range(cols):
        px, py = x0 + c*(LW+gx), y0 + r*(LH+gy)
        page.paste(lab, (px, py), lab)
        pd.rounded_rectangle((px+pad-6, py+pad-6, px+LW-pad+6, py+LH-pad+6), R+6, outline=(185, 185, 185), width=2)
ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
pd.text((PW//2, PH - y0//2), 'Print at 100% / Actual Size on glossy sticker paper  •  Cut on the gray lines  •  6 labels, 3.5" x 2.75"', font=ft, fill=(120, 120, 120), anchor='mm')
L = 2*DPI; lx = (PW-L)//2; ly = y0//2 - 10
pd.line((lx, ly, lx+L, ly), fill=(120, 120, 120), width=3); pd.line((lx, ly-12, lx, ly+12), fill=(120, 120, 120), width=3); pd.line((lx+L, ly-12, lx+L, ly+12), fill=(120, 120, 120), width=3)
pd.text((PW//2, ly+14), 'size check: this line = 2 inches', font=ft, fill=(120, 120, 120), anchor='ma')
page.save(f'{OUT}/blessed-highly-favored-candle-label-STICKER-SHEET-8.5x11-6up.png', dpi=(DPI, DPI), optimize=True)
print('ok', lab.size)
