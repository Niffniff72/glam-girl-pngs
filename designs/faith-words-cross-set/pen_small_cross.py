"""Pen wrap 5x1.5in with the WHOLE cross shrunk to fit, words pattern around it.
Usage: python3 designs/faith-words-cross-set/pen_small_cross.py <clean_up.png> <cross_mask.png>
"""
import sys, cv2, numpy as np
from PIL import Image
SRC, MASK = sys.argv[1], sys.argv[2]
OUT = 'assets/products/faith-words-cross-purple/faith-words-cross-pen-wrap-SMALL-CROSS-5x1.5in-1500x450.png'
PW, PH = 1500, 450
img = cv2.imread(SRC); H, W = img.shape[:2]                 # 3x upscale of the 1104x975 clean design
k = W / 1104.0
# cross mask (same scaling used when the cross was enlarged)
m = cv2.imread(MASK, 0); x, y, bw, bh = cv2.boundingRect(m)
nw, nh = int(bw*1.3), int(bh*1.3)
M = np.zeros(m.shape, np.uint8)
M[y+bh//2-nh//2:y+bh//2-nh//2+nh, x+bw//2-nw//2:x+bw//2-nw//2+nw] = cv2.resize(m[y:y+bh, x:x+bw], (nw, nh))
M = cv2.resize(M, (W, H), interpolation=cv2.INTER_LINEAR)
M = (M > 127).astype(np.uint8)
M = cv2.dilate(M, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(5*k), int(5*k))))   # include dark outline
cx0, cy0, cw, ch = cv2.boundingRect(M)
# --- background: cross-free strips from left/right of the design, shrunk and tiled with soft seams
SC = 0.42                                       # background scale (smaller words, sharper)
sh_src = int(PH / SC)
Lfull = img[:, :int(cx0 - 10*k)]; Rfull = img[:, int(cx0 + cw + 10*k):]
def piece(src, top):
    top = int(np.clip(top, 0, H - sh_src)); p = src[top:top+sh_src].astype(np.float32)
    return cv2.resize(p, (int(p.shape[1]*SC), PH), interpolation=cv2.INTER_AREA)
pieces = [piece(Lfull, 120), piece(Rfull, 900), piece(Lfull, 1500), piece(Rfull, 300), piece(Lfull, 800), piece(Rfull, 1700)]
ov = 40
bg = pieces[0]
for p in pieces[1:]:
    ramp = np.linspace(0, 1, ov)[None, :, None]
    blend = bg[:, -ov:]*(1-ramp) + p[:, :ov]*ramp
    bg = np.concatenate([bg[:, :-ov], blend, p[:, ov:]], axis=1)
x0 = (bg.shape[1] - PW)//2
bg = bg[:, x0:x0+PW]
# --- cross: cut out, shrink to fit the 1.5" height with a little margin
cross = img[cy0:cy0+ch, cx0:cx0+cw].astype(np.float32)
cm = M[cy0:cy0+ch, cx0:cx0+cw].astype(np.float32)
target_h = int(PH * 0.9)
s = target_h / ch
tw, th = int(cw*s), int(ch*s)
cross = cv2.resize(cross, (tw, th), interpolation=cv2.INTER_AREA)
cm = cv2.resize(cm, (tw, th), interpolation=cv2.INTER_AREA)
cm = cv2.GaussianBlur(cm, (3, 3), 0.6)[..., None]
ox, oy = (PW - tw)//2, (PH - th)//2
# soft shadow so the cross sits on top of the words
sh = np.zeros((PH, PW), np.float32); sh[oy:oy+th, ox:ox+tw] = cm[..., 0]
sh = cv2.GaussianBlur(np.roll(sh, 5, axis=0), (0, 0), 6) * 0.7
out = bg * (1 - sh[..., None])
region = out[oy:oy+th, ox:ox+tw]
out[oy:oy+th, ox:ox+tw] = region*(1-cm) + cross*cm
# gentle sharpen
blur = cv2.GaussianBlur(out, (0, 0), 1.5); out = cv2.addWeighted(out, 1.6, blur, -0.6, 0)
Image.fromarray(cv2.cvtColor(out.clip(0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).save(OUT, dpi=(300, 300), optimize=True)
print('cross', tw, 'x', th, 'px =', round(tw/300, 2), 'x', round(th/300, 2), 'in')
