import sys, cv2, numpy as np
src, out = sys.argv[1:3]
img = cv2.imread(src); h, w = img.shape[:2]
m = np.zeros((h, w), np.uint8)
m[365:373, 496:503] = 255      # notch on heart's top-left outline
m[484:498, 628:637] = 255      # notch on heart's lower-right swirl
# only replace the dark pixels inside those boxes (keep any gold already there)
v = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[..., 2]
m[(v > 110)] = 0
m = cv2.dilate(m, np.ones((3, 3), np.uint8))
print('px fixed', int((m > 0).sum()))
cv2.imwrite(out, cv2.inpaint(img, m, 4, cv2.INPAINT_TELEA))
