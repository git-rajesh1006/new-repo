"""Instagram Reel cover for Day 2. Usage: python3 make_thumbnail.py out_prefix
Writes <prefix>-reel-1080x1920.png (all key content inside the centre 4:5 safe zone, so the
profile-grid crop keeps it) and <prefix>-feed-1080x1350.png."""
import math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "/usr/share/fonts/truetype/dejavu/"
F = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s)
BG1, BG2 = (8, 10, 28), (40, 20, 86)
CY, GR, OR, PK, YE, WH, GY = (56, 212, 255), (60, 220, 130), (255, 160, 60), (255, 90, 150), (255, 220, 70), (255, 255, 255), (150, 160, 190)
mix = lambda a, b, t: tuple(int(x + (y - x) * t) for x, y in zip(a, b))

def shadow_text(im, xy, s, font, fill, anchor="mm", blur=14, off=8):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + off), s, font=font, fill=(0, 0, 0, 200), anchor=anchor)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy, s, font=font, fill=fill, anchor=anchor)

def build(W, H):
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line([0, y, W, y], fill=mix(BG1, BG2, y / H) + (255,))
    # glow blobs + dots
    for cx, cy, r, c in [(W * .85, H * .22, 420, CY), (W * .1, H * .78, 460, PK)]:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=c + (70,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(150)))
    d = ImageDraw.Draw(im)
    for i in range(60):
        x, y, r = (i * 163) % W, (i * 389) % H, 2 + i % 4
        d.ellipse([x - r, y - r, x + r, y + r], fill=mix(BG2, CY, .35) + (255,))
    # layout anchored on the vertical centre so the 4:5 crop keeps everything
    cy = H // 2
    def row(y, s, col): shadow_text(im, (W // 2, cy + y), s, F(54), col)
    # top pill
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([W // 2 - 300, cy - 590, W // 2 + 300, cy - 500], 45, fill=mix(BG1, YE, .18) + (255,), outline=YE, width=4)
    d.text((W // 2, cy - 545), "100 DAYS OF DEVOPS", font=F(40), fill=YE, anchor="mm")
    shadow_text(im, (W // 2, cy - 380), "DAY", F(190), WH)
    shadow_text(im, (W // 2, cy - 120), "2", F(330), CY, blur=22)
    shadow_text(im, (W // 2, cy + 110), "DevOps Engineer", F(96), WH)
    shadow_text(im, (W // 2, cy + 230), "em chestadu?", F(112), OR)
    # flow chips: Code -> Build -> Deploy -> Monitor
    d = ImageDraw.Draw(im)
    chips = [("Code", PK), ("Test", YE), ("Deploy", GR), ("Monitor", CY)]
    cw, gap = 200, 40
    x0 = (W - (4 * cw + 3 * gap)) // 2
    for i, (s, c) in enumerate(chips):
        x = x0 + i * (cw + gap)
        d.rounded_rectangle([x, cy + 330, x + cw, cy + 420], 30, fill=mix(BG1, c, .25) + (255,), outline=c, width=4)
        d.text((x + cw // 2, cy + 375), s, font=F(38), fill=WH, anchor="mm")
        if i < 3:
            ax = x + cw + gap // 2
            d.polygon([(ax - 10, cy + 360), (ax + 12, cy + 375), (ax - 10, cy + 390)], fill=WH)
    # tools row
    d.text((W // 2, cy + 500), "Git  •  Jenkins  •  Docker  •  Kubernetes  •  AWS", font=F(34), fill=GY, anchor="mm")
    # watch badge
    d.rounded_rectangle([W // 2 - 230, cy + 560, W // 2 + 230, cy + 640], 40, fill=PK + (255,))
    d.text((W // 2, cy + 600), "WATCH NOW", font=F(44), fill=WH, anchor="mm")
    return im.convert("RGB")

if __name__ == "__main__":
    p = sys.argv[1]
    build(1080, 1920).save(p + "-reel-1080x1920.png")
    # feed/grid version: crop the centre 4:5 band from the same design
    build(1080, 1920).crop((0, 285, 1080, 1635)).save(p + "-feed-1080x1350.png")
