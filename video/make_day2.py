"""Render Day 2 (DevOps Engineer Em Chestadu?) as a 1080x1920, 60s vertical video.
Usage: python3 make_day2.py out.mp4   (needs Pillow, numpy, ffmpeg)
"""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 60
FD = "/usr/share/fonts/truetype/dejavu/"
def F(sz, bold=True): return ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)
FM = lambda sz: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", sz)

BG1, BG2 = (10, 14, 32), (24, 18, 60)
CY, GR, OR, PK, YE, WH, GY = (56, 212, 255), (60, 220, 130), (255, 160, 60), (255, 90, 150), (255, 220, 70), (255, 255, 255), (150, 160, 190)

# (start, end, [caption chunks]) — captions follow the script
SCENES = [
 (0, 5,  ["Day 1 lo DevOps ante enti telusukunnam kada!", "Mari aa process ni real ga implement chese", "DevOps Engineer em chestadu?"]),
 (5, 15, ["DevOps Engineer main ga developers create chesina application ni", "testing nunchi deployment varaku", "smooth ga, automatic ga run ayyela help chestadu."]),
 (15, 28, ["Developer code ni GitHub lo push chesinappudu,", "CI/CD pipeline automatic ga code ni test chesi,", "build chesi, deployment process ni easy chestundi."]),
 (28, 40, ["Dinikosam Git, Jenkins, Docker, Kubernetes, AWS", "laanti tools use chestaru.", "Prathi tool ki oka specific purpose untundi."]),
 (40, 50, ["Application deploy chesina tarvata kuda", "DevOps Engineer pani complete kaadu!", "Errors emaina vasthunnaya ani monitor chestadu."]),
 (50, 60, ["DevOps Engineer = automation, deployment,", "cloud infrastructure, monitoring.", "Repu Day 3 lo DevOps Lifecycle! Follow avvandi!"]),
]

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def bg(t):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 6):
        d.rectangle([0, y, W, y + 6], fill=mix(BG1, BG2, y / H))
    # drifting dots
    for i in range(24):
        x = (i * 97 + t * 15 * (1 + i % 3)) % W
        y = (i * 211 + t * 25) % H
        r = 3 + i % 4
        d.ellipse([x - r, y - r, x + r, y + r], fill=mix(BG2, CY, 0.25))
    return im, d

def ctext(d, xy, s, font, fill, anchor="mm"): d.text(xy, s, font=font, fill=fill, anchor=anchor)

def rbox(d, box, fill, outline=None, r=36, w=4): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=w)

def node(d, cx, cy, label, col, sc=1.0, sub=None, size=190):
    s = int(size * sc)
    if s < 10: return
    rbox(d, [cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], mix(BG1, col, 0.22), col, 30, 5)
    ctext(d, (cx, cy - (14 if sub else 0)), label, F(int(34 * sc)), WH)
    if sub: ctext(d, (cx, cy + 40 * sc), sub, F(int(24 * sc), False), col)

def arrow(d, x1, y1, x2, y2, col, prog=1.0):
    ex, ey = lerp(x1, x2, prog), lerp(y1, y2, prog)
    d.line([x1, y1, ex, ey], fill=col, width=8)
    if prog > 0.95:
        a = math.atan2(y2 - y1, x2 - x1)
        for da in (2.6, -2.6):
            d.line([x2, y2, x2 + 30 * math.cos(a + da), y2 + 30 * math.sin(a + da)], fill=col, width=8)

def title(d, s, sub, t0, t):
    p = ease((t - t0) / 0.6)
    ctext(d, (W / 2, 250 - (1 - p) * 40), s, F(78), mix(BG1, WH, p))
    ctext(d, (W / 2, 335), sub, F(38, False), mix(BG1, CY, p))

# ---------- scenes ----------
def s_hook(d, t):
    p = ease(t / 0.8)
    ctext(d, (W / 2, 520 - (1 - p) * 120), "DAY 2", F(210), mix(BG1, CY, p))
    ctext(d, (W / 2, 720), "100 Days of DevOps", F(52), mix(BG1, YE, ease((t - .3) / .6)))
    rbox(d, [140, 860, 940, 1000], mix(BG1, WH, .08 * ease((t - .8) / .5)), CY, 40, 4)
    q = ease((t - 1.0) / .6)
    ctext(d, (W / 2, 930), "DevOps Engineer", F(72), mix(BG1, WH, q))
    ctext(d, (W / 2, 1110), "em chestadu?", F(100), mix(BG1, OR, ease((t - 1.6) / .6)))
    # Day1 -> Day2 chip
    node(d, 330, 1360, "Day 1", GY, ease((t - 2) / .5), "DevOps ante?", 230)
    arrow(d, 450, 1360, 630, 1360, CY, ease((t - 2.5) / .8))
    node(d, 750, 1360, "Day 2", CY, ease((t - 3) / .5), "Role", 230)

def s_role(d, t):
    title(d, "DevOps Engineer", "Bridge: Dev  ->  Production", 0, t)
    y = 800
    node(d, 190, y, "Dev", PK, ease(t / .6), "code")
    node(d, 540, y, "DevOps", CY, ease((t - .8) / .6), "Engineer", 240)
    node(d, 890, y, "Prod", GR, ease((t - 1.6) / .6), "users")
    arrow(d, 290, y, 410, y, CY, ease((t - 1.2) / .6))
    arrow(d, 670, y, 790, y, CY, ease((t - 2.0) / .6))
    # steps
    steps = ["Testing", "Build", "Deploy"]
    for i, s in enumerate(steps):
        p = ease((t - 3 - i * .8) / .5)
        x = 190 + i * 350
        rbox(d, [x - 140, 1130, x + 140, 1250], mix(BG1, OR, .25 * p), mix(BG1, OR, p), 28)
        ctext(d, (x, 1190), s, F(44), mix(BG1, WH, p))
    ctext(d, (W / 2, 1400), "smooth + automatic", F(60), mix(BG1, YE, ease((t - 6) / .6)))

def s_pipeline(d, t):
    title(d, "CI/CD Pipeline", "Push  ->  Test  ->  Build  ->  Deploy", 0, t)
    stages = [("GitHub", "push", PK), ("Test", "auto", YE), ("Build", "auto", OR), ("Deploy", "auto", GR)]
    ys = [600, 850, 1100, 1350]
    for i, (n, sub, c) in enumerate(stages):
        a = 1.0 + i * 2.6
        p = ease((t - a) / .5)
        node(d, 330, ys[i], n, c, p, None, 190)
        done = ease((t - a - 1.2) / .6)
        # progress bar
        bx = 480
        rbox(d, [bx, ys[i] - 22, bx + 480, ys[i] + 22], mix(BG1, WH, .08 * p), None, 22)
        if p > 0:
            rbox(d, [bx, ys[i] - 22, bx + max(1, 480 * done), ys[i] + 22], c, None, 22)
        if done >= 1:
            ctext(d, (bx + 440, ys[i] + 62), "OK", F(34), GR)
        if i < 3:
            arrow(d, 330, ys[i] + 95, 330, ys[i + 1] - 95, c, ease((t - a - 1.8) / .6))
    ctext(d, (W / 2, 1530), "Sab automatic!", F(58), mix(BG1, YE, ease((t - 11.5) / .5)))

def s_tools(d, t):
    title(d, "DevOps Tools", "Prathi tool ki oka purpose", 0, t)
    tools = [("Git", "Version control", PK), ("Jenkins", "CI/CD automation", OR), ("Docker", "Containers", CY),
             ("Kubernetes", "Orchestration", (90, 140, 255)), ("AWS", "Cloud", YE)]
    for i, (n, sub, c) in enumerate(tools):
        p = ease((t - .8 - i * 1.8) / .5)
        y = 560 + i * 225
        x = lerp(W + 400, 0, p)
        rbox(d, [110 + x, y - 90, 970 + x, y + 90], mix(BG1, c, .2), c, 34, 5)
        d.ellipse([150 + x, y - 55, 260 + x, y + 55], fill=c)
        ctext(d, (205 + x, y), n[0], F(60), BG1)
        ctext(d, (300 + x, y - 24), n, F(54), WH, "lm")
        ctext(d, (300 + x, y + 36), sub, F(32, False), c, "lm")

def s_monitor(d, t):
    title(d, "Monitoring", "Deploy tarvata kuda pani untundi", 0, t)
    rbox(d, [90, 520, 990, 1150], mix(BG1, WH, .05), CY, 36)
    for k in range(1, 5):
        d.line([130, 520 + k * 126, 950, 520 + k * 126], fill=mix(BG1, WH, .12), width=2)
    pts = []
    for i in range(60):
        x = 140 + i * 13.5
        v = 0.5 + .12 * math.sin(i * .5) + .05 * math.sin(i * 1.7)
        if 36 < i < 44: v += .35 * math.exp(-((i - 40) ** 2) / 4)  # error spike
        pts.append((x, 1100 - v * 520))
    n = int(len(pts) * min(1, t / 7))
    spike = 36 * 13.5 / 13.5 / 60 < (n / 60)
    for a, b in zip(pts[:max(0, n - 1)], pts[1:n]):
        bad = b[1] < 800
        d.line([a, b], fill=PK if bad else GR, width=7)
    status_bad = n > 37 and n < 49
    # status pills
    items = [("Server", GR), ("Errors", PK if status_bad else GR), ("Logs", GR)]
    for i, (s, c) in enumerate(items):
        x = 200 + i * 340
        rbox(d, [x - 140, 1230, x + 140, 1330], mix(BG1, c, .25), c, 30)
        d.ellipse([x - 110, 1268, x - 86, 1292], fill=c)
        ctext(d, (x + 15, 1280), s, F(38), WH)
    if status_bad:
        a = .5 + .5 * math.sin(t * 9)
        ctext(d, (W / 2, 1450), "ALERT! Error detected", F(54), mix(BG1, PK, .5 + .5 * a))
    elif n >= 49:
        ctext(d, (W / 2, 1450), "Fixed - sab healthy", F(54), GR)

def s_recap(d, t):
    ctext(d, (W / 2, 250), "DevOps Engineer =", F(70), WH)
    items = [("Automation", CY), ("Deployment", OR), ("Cloud Infra", YE), ("Monitoring", GR)]
    for i, (s, c) in enumerate(items):
        p = ease((t - .5 - i * .9) / .5)
        y = 440 + i * 170
        rbox(d, [140 + (1 - p) * 900, y - 70, 940 + (1 - p) * 900, y + 70], mix(BG1, c, .22), c, 34)
        ctext(d, (W / 2 + (1 - p) * 900, y), s, F(62), WH)
    p = ease((t - 5) / .6)
    pulse = 1 + .04 * math.sin(t * 6)
    w = 420 * pulse
    rbox(d, [W / 2 - w, 1190, W / 2 + w, 1320], mix(BG1, PK, p), None, 60)
    ctext(d, (W / 2, 1255), "FOLLOW", F(72), mix(BG1, WH, p))
    ctext(d, (W / 2, 1410), "Day 3: DevOps Lifecycle", F(58), mix(BG1, YE, ease((t - 6.5) / .6)))
    ctext(d, (W / 2, 1490), "repu!", F(48, False), mix(BG1, CY, ease((t - 7) / .6)))

RENDER = [s_hook, s_role, s_pipeline, s_tools, s_monitor, s_recap]

def caption(d, t):
    for (a, b, chunks), _ in zip(SCENES, RENDER):
        if a <= t < b:
            seg = (b - a) / len(chunks)
            i = min(len(chunks) - 1, int((t - a) / seg))
            lines = chunks[i]
            # wrap at ~28 chars
            words, ln, out = lines.split(), "", []
            for w_ in words:
                if len(ln) + len(w_) > 30: out.append(ln); ln = w_
                else: ln = (ln + " " + w_).strip()
            out.append(ln)
            h = 70 * len(out) + 40
            top = 1790 - h
            rbox(d, [50, top, 1030, 1830], (0, 0, 0), None, 30)
            for k, o in enumerate(out):
                ctext(d, (W / 2, top + 55 + k * 70), o, F(46), WH)

def frame(fi):
    t = fi / FPS
    im, d = bg(t)
    for k, (a, b, _) in enumerate(SCENES):
        if a <= t < b:
            RENDER[k](d, t - a)
            # scene fade
            lt = t - a
            if lt < .3 or b - t < .3:
                f = min(lt, b - t) / .3
                ov = Image.new("RGB", (W, H), BG1)
                im = Image.blend(ov, im, max(0, f))
                d = ImageDraw.Draw(im)
    # top progress bar + brand
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W * t / DUR, 12], fill=CY)
    ctext(d, (W / 2, 70), "100 DAYS OF DEVOPS", F(30), GY)
    caption(d, t)
    return im

def main(out):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                          "-t", str(DUR), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
                          "-c:a", "aac", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(FPS * DUR):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "day2.mp4")
