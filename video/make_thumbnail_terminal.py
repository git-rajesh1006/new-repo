"""Thumbnail template for the 100 Days of DevOps series (terminal / black + neon-green style).
Usage: python3 make_thumbnail.py <day>      -> day<N>-thumbnail-1080x1920.png
Add a new day by adding an entry to DAYS."""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FD = "/usr/share/fonts/truetype/dejavu/"
SANS = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s)
MONO = lambda s: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", s)
BG, GRID, GREEN, WHITE, OFFWHITE, GREY = (10, 10, 10), (20, 20, 20), (0, 255, 160), (255, 255, 255), (244, 244, 244), (110, 110, 110)

DAYS = {
    1: dict(white="WHAT IS", green="DEVOPS?", term=[
        ("$ git push origin main", WHITE), ("> build", "OK"), ("> 24 tests", "PASSED"), ("> deploy", "LIVE")]),
    2: dict(white="DEVOPS ENGINEER", green="EM CHESTADU?", term=[
        ("$ git push origin main", WHITE), ("> test", "PASSED"), ("> deploy", "LIVE"), ("> monitor", "HEALTHY")]),
}

def fit(text, font, max_w, cap):
    s = cap
    while font(s).getlength(text) > max_w: s -= 2
    return font(s)

def build(day):
    cfg = DAYS[day]
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 90): d.line([x, 0, x, H], fill=GRID)
    for y in range(0, H, 90): d.line([0, y, W, y], fill=GRID)
    # header, letter-spaced
    hdr, f = "100 DAYS OF DEVOPS", MONO(36)
    sp = 5; tw = sum(f.getlength(c) + sp for c in hdr) - sp; x = (W - tw) / 2
    for c in hdr:
        d.text((x, 170), c, font=f, fill=GREY, anchor="lm"); x += f.getlength(c) + sp
    d.text((W / 2, 455), f"DAY {day}", font=fit(f"DAY {day}", MONO, 975, 336), fill=WHITE, anchor="mm")
    d.text((W / 2, 780), cfg["white"], font=fit(cfg["white"], SANS, 990, 158), fill=OFFWHITE, anchor="mm")
    d.text((W / 2, 955), cfg["green"], font=fit(cfg["green"], SANS, 990, 205), fill=GREEN, anchor="mm")
    # terminal card
    d.rounded_rectangle([140, 1150, 940, 1450], 40, fill=(0, 0, 0), outline=(40, 40, 40), width=3)
    tf = MONO(44)
    for i, (a, b) in enumerate(cfg["term"]):
        y = 1222 + i * 64
        if i == 0:
            d.text((187, y), a, font=tf, fill=b, anchor="lm")
        else:
            dots = " " + "." * max(3, 14 - len(a) - 1) + " "
            d.text((187, y), a + dots + b, font=tf, fill=GREEN, anchor="lm")
    # pill
    d.rounded_rectangle([336, 1540, 745, 1643], 52, fill=GREEN)
    d.text((540, 1591), "IN TELUGU", font=MONO(52), fill=(0, 0, 0), anchor="mm")
    return im

if __name__ == "__main__":
    n = int(sys.argv[1]); build(n).save(f"day{n}-thumbnail-1080x1920.png")
