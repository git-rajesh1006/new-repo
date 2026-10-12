"""Extract reusable image assets from the reference frames (frames dumped by ffmpeg at 30 fps: f_0001 = t0)."""
import sys, numpy as np, cv2
from PIL import Image
FR = sys.argv[1]; OUT = sys.argv[2]
def fr(t): return cv2.imread(f"{FR}/f_{int(round(t * 30)) + 1:04d}.jpg")
def save(name, img): cv2.imwrite(f"{OUT}/{name}.png", img)

# full-frame website designs (third-party designs shown in the ad)
save("site_browser_history", fr(24.5)); save("site_never_stop", fr(27.0))
# laptop-in-clouds plate (clean frame, UI on screen is "Claude / Build something beautiful.")
save("plate_laptop", fr(34.0))
# mountains plate with the "What if" text removed (inpaint the whole text box; background there is smooth sky)
m = fr(0.5); reg = np.zeros(m.shape[:2], np.uint8); reg[535:625, 465:765] = 255
save("plate_mountains", cv2.inpaint(m, reg, 7, cv2.INPAINT_TELEA))
save("plate_sky", fr(0.0))
# website cards cropped from the "Every day, people pay thousands" shot
f = fr(17.0); horse = f[301:597, 332:790].copy()
mask = np.zeros(horse.shape[:2], np.uint8); mask[28:56, 175:210] = 255   # mouse cursor
save("card_horse", cv2.inpaint(horse, mask, 4, cv2.INPAINT_TELEA))
save("card_haven", f[327:575, 0:326]); save("card_ai", fr(16.0)[314:534, 700:994])
# author avatar (circular crop) from the closing shot
a = fr(53.0)[105:335, 525:755]; save("avatar", a)
print("assets written")
