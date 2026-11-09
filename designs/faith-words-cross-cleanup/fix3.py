import sys, cv2, numpy as np
src, mask_path, out = sys.argv[1:4]
img = cv2.imread(src).astype(np.float32); h, w = img.shape[:2]
m = cv2.imread(mask_path, 0); x, y, bw, bh = cv2.boundingRect(m)
nw, nh = int(bw*1.3), int(bh*1.3)
M2 = np.zeros((h, w), np.uint8)
M2[y+bh//2-nh//2:y+bh//2-nh//2+nh, x+bw//2-nw//2:x+bw//2-nw//2+nw] = cv2.resize(m[y:y+bh, x:x+bw], (nw, nh))
M2 = (M2 > 127).astype(np.uint8)
inside = cv2.erode(M2, np.ones((9, 9), np.uint8))          # true cross body (keep its outline)
hsv = cv2.cvtColor(img.clip(0,255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(int)
gold = (hsv[...,0] >= 8) & (hsv[...,0] <= 38) & (hsv[...,1] > 40) & (hsv[...,2] > 70)
# 1) gold specks sitting just above the left arm, outside the cross body
zone = np.zeros((h, w), bool); zone[340:392, 286:500] = True
outline = cv2.dilate(M2, np.ones((5, 5), np.uint8)) & (1 - inside)
specks = (gold & zone & (inside == 0)).astype(np.uint8)
specks[(outline == 1) & (np.arange(h)[:, None] > 380)] = 0     # keep the real arm edge
specks = cv2.dilate(specks, np.ones((5, 5), np.uint8)) & (1 - inside)
print('speck px', int(specks.sum()))
rng = np.random.default_rng(8)
ref = img[522:562, 362:462].reshape(-1, 3)
dark = ref[ref.max(1) < np.percentile(ref.max(1), 70)]
mu, sd = dark.mean(0), dark.std(0)
ys, xs = np.nonzero(specks)
img[ys, xs] = mu + rng.normal(0, 1, (len(ys), 3)) * sd * 1.6
# 2) brighten the flat dark smudges under the arms with fine glitter
def glitter(y0, y1, x0, x1, count):
    for _ in range(count):
        yy, xx = rng.integers(y0, y1), rng.integers(x0, x1)
        if inside[yy, xx]: continue
        col = np.array(rng.choice([[235, 230, 245], [250, 210, 235], [210, 190, 255], [200, 230, 255]]), np.float32)
        r = rng.choice([0.6, 0.8, 1.0, 1.2])
        a0, a1, b0, b1 = max(yy-3,0), min(yy+4,h), max(xx-3,0), min(xx+4,w)
        gy, gx = np.mgrid[a0:a1, b0:b1]
        g = (np.exp(-((gy-yy)**2 + (gx-xx)**2) / (2*r*r)) * rng.uniform(0.5, 1.0))[..., None]
        g[inside[a0:a1, b0:b1] == 1] = 0
        img[a0:a1, b0:b1] = np.maximum(img[a0:a1, b0:b1], g * col)
glitter(336, 396, 280, 505, 60)     # above left arm
glitter(492, 512, 370, 490, 14)      # under left arm
glitter(488, 512, 630, 730, 14)      # under right arm
# 3) twinkle stars (4-point) like the ones already in the design
def star(cx, cy, size, col=(225, 240, 255), core=1.0):
    col = np.array(col, np.float32)
    R = int(size * 1.2)
    a0, a1, b0, b1 = max(cy-R,0), min(cy+R+1,h), max(cx-R,0), min(cx+R+1,w)
    gy, gx = np.mgrid[a0:a1, b0:b1].astype(np.float32); dy, dx = gy-cy, gx-cx
    ray = np.exp(-(dx**2)/(2*0.9**2)) * np.exp(-np.abs(dy)/(size*0.35)) + \
          np.exp(-(dy**2)/(2*0.9**2)) * np.exp(-np.abs(dx)/(size*0.35))
    glow = np.exp(-(dx**2 + dy**2) / (2*(size*0.18)**2)) * core
    val = np.clip(ray*0.9 + glow, 0, 1)[..., None]
    val[inside[a0:a1, b0:b1] == 1] = 0
    img[a0:a1, b0:b1] = img[a0:a1, b0:b1]*(1-val) + col*val
star(360, 372, 16)              # right over the old specks
star(452, 360, 11, core=0.8)
star(318, 392, 9, col=(255, 220, 240), core=0.7)
star(420, 503, 8, core=0.7)     # under left arm
star(688, 500, 9, core=0.7)     # under right arm
cv2.imwrite(out, img.clip(0, 255).astype(np.uint8))
