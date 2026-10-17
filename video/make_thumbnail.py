"""Instagram thumbnail, 'big number + chips' layout in the black / neon-green palette.
Usage: python3 make_thumbnail.py <day>  -> day<N>-thumbnail-reel-1080x1920.png and day<N>-thumbnail-feed-1080x1350.png
(the feed file is the centre 4:5 crop of the reel cover). Add new days to DAYS."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "/usr/share/fonts/truetype/dejavu/"
F = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s)
M = lambda s: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", s)
BG, GRID, GREEN, WHITE, GREY, BLACK = (10, 10, 10), (20, 20, 20), (0, 255, 160), (255, 255, 255), (110, 110, 110), (0, 0, 0)
mix = lambda a, b, t: tuple(int(x + (y - x) * t) for x, y in zip(a, b))

DAYS = {
    2: dict(white="DevOps Engineer", green="em chestadu?", chips=["Code", "Test", "Deploy", "Monitor"],
            tools="Git  •  Jenkins  •  Docker  •  Kubernetes  •  AWS"),
    6: dict(white="SDLC", green="Life Cycle", chips=["Plan", "Design & Dev", "Test", "Deploy", "Maintain"], tools=None, cw=300, cf=36, per=3),
    5: dict(white="Agile & DevOps", green="Connection?", chips=["Small steps", "Feedback", "Improve"], tools=None, cw=300, cf=36, per=3),
    4: dict(white="Traditional IT", green="vs DevOps", chips=["Collaboration", "Automation", "Improvement"], tools=None, cw=300, cf=34, per=3),
    3: dict(white="DevOps", green="Lifecycle", chips=["Plan", "Code", "Build", "Test", "Release", "Deploy", "Operate", "Monitor"],
            tools=None),
}

def shadow_text(im, xy, s, font, fill, blur=14, off=8):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + off), s, font=font, fill=(0, 0, 0, 230), anchor="mm")
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy, s, font=font, fill=fill, anchor="mm")

def fit(text, max_w, cap):
    s = cap
    while F(s).getlength(text) > max_w: s -= 2
    return F(s)

def build(day):
    cfg, W, H = DAYS[day], 1080, 1920
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 90): d.line([x, 0, x, H], fill=GRID)
    for y in range(0, H, 90): d.line([0, y, W, y], fill=GRID)
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))   # soft green glow behind the number
    ImageDraw.Draw(g).ellipse([140, 560, 940, 1360], fill=GREEN + (55,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(170)))
    cy = H // 2
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([W // 2 - 300, cy - 590, W // 2 + 300, cy - 500], 45, fill=BLACK + (255,), outline=GREEN, width=4)
    d.text((W // 2, cy - 545), "100 DAYS OF DEVOPS", font=F(40), fill=GREEN, anchor="mm")
    shadow_text(im, (W // 2, cy - 380), "DAY", F(190), WHITE)
    shadow_text(im, (W // 2, cy - 120), str(day), F(330), GREEN, blur=22)
    shadow_text(im, (W // 2, cy + 110), cfg["white"], fit(cfg["white"], 930, 96), WHITE)
    shadow_text(im, (W // 2, cy + 230), cfg["green"], fit(cfg["green"], 930, 112), GREEN)
    d = ImageDraw.Draw(im)
    per, cw, gap, y0 = cfg.get("per", 4), cfg.get("cw", 200), 40, cy + 330
    chips = cfg["chips"]
    rows = [chips[i:i + per] for i in range(0, len(chips), per)]
    for r, row in enumerate(rows):
        n = len(row)
        x0 = (W - (n * cw + (n - 1) * gap)) // 2
        ry = y0 + r * 120
        for i, s in enumerate(row):
            x = x0 + i * (cw + gap)
            final = r == len(rows) - 1 and i == n - 1
            d.rounded_rectangle([x, ry, x + cw, ry + 90], 30, fill=GREEN if final else BLACK, outline=GREEN, width=4)
            d.text((x + cw // 2, ry + 45), s, font=F(cfg.get("cf", 38)), fill=BLACK if final else WHITE, anchor="mm")
            if i < n - 1:
                ax = x + cw + gap // 2
                d.polygon([(ax - 10, ry + 30), (ax + 12, ry + 45), (ax - 10, ry + 60)], fill=GREEN)
    wy = y0 + len(rows) * 120 + (50 if not cfg["tools"] else 0)
    if cfg["tools"]:
        d.text((W // 2, y0 + 170), cfg["tools"], font=F(34), fill=GREY, anchor="mm")
        wy = y0 + 230
    d.rounded_rectangle([W // 2 - 230, wy, W // 2 + 230, wy + 80], 40, fill=GREEN)
    d.text((W // 2, wy + 40), "WATCH NOW", font=M(44), fill=BLACK, anchor="mm")
    return im.convert("RGB")

if __name__ == "__main__":
    n = int(sys.argv[1]); im = build(n)
    im.save(f"day{n}-thumbnail-reel-1080x1920.png")
    im.crop((0, 285, 1080, 1635)).save(f"day{n}-thumbnail-feed-1080x1350.png")
