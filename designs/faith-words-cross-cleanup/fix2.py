import sys, cv2, numpy as np
src, mask_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
img = cv2.imread(src); orig = img.copy(); h, w = img.shape[:2]
m = cv2.imread(mask_path, 0); x, y, bw, bh = cv2.boundingRect(m)
nw, nh = int(bw*1.3), int(bh*1.3)
M2 = np.zeros((h, w), np.uint8)
M2[y+bh//2-nh//2:y+bh//2-nh//2+nh, x+bw//2-nw//2:x+bw//2-nw//2+nw] = cv2.resize(m[y:y+bh, x:x+bw], (nw, nh))
M2 = (M2 > 127).astype(np.uint8)
protect = cv2.dilate(M2, np.ones((5, 5), np.uint8))
# target zone: left of / above the left arm
zone = np.zeros((h, w), np.uint8); zone[350:413, 296:488] = 1
remove = (zone & (1 - protect)).astype(np.uint8)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
words = (((hsv[...,0] >= 10) & (hsv[...,0] <= 35) & (hsv[...,1] > 50) & (hsv[...,2] > 100)) |
         ((hsv[...,0] >= 120) & (hsv[...,0] <= 165) & (hsv[...,1] > 70) & (hsv[...,2] > 70))).astype(np.uint8)
bg_ok = (cv2.dilate(words, np.ones((9, 9), np.uint8)) == 0) & (cv2.dilate(M2, np.ones((9, 9), np.uint8)) == 0)
bg_ok[300:420, 290:500] = False  # don't copy from the messy area itself
# also require source to look like glitter (not the dark blotches): local std high enough
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
std = np.sqrt(np.maximum(cv2.blur(gray*gray, (9, 9)) - cv2.blur(gray, (9, 9))**2, 0))
bg_ok &= std > 9
# synthetic glitter matched to the surrounding background
rng = np.random.default_rng(21)
REF = (slice(522, 562), slice(362, 462))
ref = orig[REF].reshape(-1, 3).astype(np.float32)   # clean glitter just below-left of the arm
V = ref.max(axis=1)
dark = ref[V < np.percentile(V, 70)]
base_mu, base_sd = ref.mean(0)*0.85, dark.std(0)
bright = ref[V > np.percentile(V, 93)]
print('dark px', len(dark), 'bright px', len(bright), 'base', base_mu.round(1))
zy0, zy1, zx0, zx1 = 340, 422, 286, 498
ZH, ZW = zy1 - zy0, zx1 - zx0
tex = base_mu + rng.normal(0, 1, (ZH, ZW, 3)) * base_sd * 1.7
tex = cv2.GaussianBlur(tex.astype(np.float32), (3, 3), 0.6)
# sparkle density measured from the reference patch
refg = cv2.cvtColor(orig[REF], cv2.COLOR_BGR2GRAY)
peaks = (refg > np.percentile(refg, 90)) & (refg == cv2.dilate(refg, np.ones((3, 3), np.uint8)))
dens = peaks.sum() / refg.size
n = int(dens * ZH * ZW * 2.2)
print('sparkles', n)
spark = np.zeros((ZH, ZW, 3), np.float32)
for _ in range(n):
    yy, xx = rng.integers(0, ZH), rng.integers(0, ZW)
    col = bright[rng.integers(len(bright))] if len(bright) else np.array([200, 200, 220], np.float32)
    r = rng.choice([0.6, 0.8, 1.0, 1.3])
    y0, y1, x0, x1 = max(yy-3, 0), min(yy+4, ZH), max(xx-3, 0), min(xx+4, ZW)
    gy, gx = np.mgrid[y0:y1, x0:x1]
    g = np.exp(-((gy-yy)**2 + (gx-xx)**2) / (2*r*r))[..., None]
    spark[y0:y1, x0:x1] = np.maximum(spark[y0:y1, x0:x1], g * col)
tex = np.maximum(tex, spark)
region = img[zy0:zy1, zx0:zx1].astype(np.float32)
rm = remove[zy0:zy1, zx0:zx1].astype(bool)
region[rm] = tex[rm]
img[zy0:zy1, zx0:zx1] = region.clip(0, 255).astype(np.uint8)
soft = cv2.GaussianBlur(remove.astype(np.float32), (15, 15), 0)[..., None]
soft = np.minimum(soft*1.6, 1.0)
soft[protect[..., None].repeat(1, 2) == 1] = 0
res = img.astype(np.float32)*soft + orig.astype(np.float32)*(1-soft)
cv2.imwrite(out, res.clip(0, 255).astype(np.uint8))
