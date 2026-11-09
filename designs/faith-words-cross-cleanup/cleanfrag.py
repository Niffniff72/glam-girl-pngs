import sys, cv2, numpy as np
comp, mask_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
SCALE = 1.3
img = cv2.imread(comp); h, w = img.shape[:2]
m = cv2.imread(mask_path, 0)
x, y, bw, bh = cv2.boundingRect(m)
nw, nh = int(bw*SCALE), int(bh*SCALE)
mc = cv2.resize(m[y:y+bh, x:x+bw], (nw, nh))
M2 = np.zeros((h, w), np.uint8)
cx, cy = x+bw//2, y+bh//2; nx, ny = cx-nw//2, cy-nh//2
M2[ny:ny+nh, nx:nx+nw] = mc
M2 = (M2 > 127).astype(np.uint8)
rows = np.where((M2.sum(axis=1) > 0.6*nw))[0]
arm_top, arm_bot = rows.min(), rows.max()
print('arm band', arm_top, arm_bot)
halo = cv2.dilate(M2, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))) & (1-M2)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
H, Sa, V = hsv[...,0].astype(int), hsv[...,1].astype(int), hsv[...,2].astype(int)
purple = (H >= 120) & (H <= 165) & (Sa > 70) & (V > 70)
gold = (H >= 10) & (H <= 35) & (Sa > 50) & (V > 100)
words = ((purple | gold) & (M2 == 0)).astype(np.uint8)
joined = cv2.dilate(words, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(joined)
remove = np.zeros((h, w), np.uint8); kept = 0; removed = 0
for i in range(1, n):
    comp_m = (lab == i)
    area = comp_m.sum()
    if area < 30: continue
    inside = (comp_m & (halo == 1)).sum() / area
    touches = (cv2.dilate(comp_m.astype(np.uint8), np.ones((3,3),np.uint8)) & M2).any()
    cy_ = np.where(comp_m)[0].mean()
    in_band = (arm_top - 70) <= cy_ <= (arm_bot + 90)
    if inside > 0.55 and touches and in_band:
        remove |= comp_m.astype(np.uint8); removed += 1
    elif touches: kept += 1
remove = cv2.dilate(remove, np.ones((5, 5), np.uint8)) & (1-M2)
print('fragments removed', removed, 'touching words kept', kept, 'px', int(remove.sum()))
# fill removed pixels with real glitter copied from nearby clean background
bg_ok = ((cv2.dilate(words, np.ones((9, 9), np.uint8)) == 0) & (cv2.dilate(M2, np.ones((9,9),np.uint8)) == 0) & (remove == 0))
base = img.copy(); todo = remove.astype(bool).copy()
offsets = [(dy, dx) for r in (30, 45, 60, 80, 100, 130) for dy, dx in
           ((0, r), (0, -r), (r, 0), (-r, 0), (r, r), (-r, -r), (r, -r), (-r, r))]
ys, xs = np.nonzero(todo)
for dy, dx in offsets:
    if not len(ys): break
    sy, sx = ys + dy, xs + dx
    ok = (sy >= 0) & (sy < h) & (sx >= 0) & (sx < w)
    ok[ok] = bg_ok[sy[ok], sx[ok]]
    base[ys[ok], xs[ok]] = img[sy[ok], sx[ok]]
    ys, xs = ys[~ok], xs[~ok]
if len(ys):
    inp = cv2.inpaint(img, remove*255, 5, cv2.INPAINT_TELEA); base[ys, xs] = inp[ys, xs]
# soften the seam
soft = cv2.GaussianBlur(remove.astype(np.float32), (7, 7), 0)[..., None]
base = (base.astype(np.float32)*soft + img.astype(np.float32)*(1-soft))
base[remove == 1] = base[remove == 1]
cv2.imwrite(out, base.clip(0, 255).astype(np.uint8))
cv2.imwrite(out.replace('.png', '-removed.png'), remove*255)
