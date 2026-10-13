"""Render Day 2 (DevOps Engineer Em Chestadu?) as a 1080x1920 vertical video synced to a voiceover.
Usage: python3 make_day2.py voiceover.mp3 out.mp4   (needs Pillow, numpy, ffmpeg)

Sync: sentence windows below were measured from the voiceover with ffmpeg silencedetect
(-32dB, 0.1s). Word times inside a sentence are estimated by letter count and snapped to
nearby mid-sentence pauses; every visual cue and caption is keyed to a word via wt().
"""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 61.231
FD = "/usr/share/fonts/truetype/dejavu/"
def F(sz, bold=True): return ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)
FM = lambda sz: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", sz)

BG1, BG2 = (10, 14, 32), (24, 18, 60)
CY, GR, OR, PK, YE, WH, GY = (56, 212, 255), (60, 220, 130), (255, 160, 60), (255, 90, 150), (255, 220, 70), (255, 255, 255), (150, 160, 190)

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


# ---------------- audio sync data ----------------
# (speech start, speech end, text) per sentence, measured from the voiceover
SENT = [
 (0.21, 3.04,  "Day 1 lo DevOps ante enti telusukunnam kada!"),
 (3.43, 8.41,  "Mari aa process ni real ga implement chese DevOps Engineer em chestadu?"),
 (8.86, 17.49, "DevOps Engineer main ga developers create chesina application ni testing nunchi deployment varaku smooth ga, automatic ga run ayyela help chestadu."),
 (18.00, 29.23, "Example ki, developer code ni GitHub lo push chesinappudu, DevOps Engineer setup chesina CI/CD pipeline automatic ga code ni test chesi, build chesi, deployment process ni easy chestundi."),
 (29.56, 35.62, "Dinikosam Git, Jenkins, Docker, Kubernetes, AWS laanti tools use chestaru."),
 (36.04, 38.49, "Prathi tool ki oka specific purpose untundi."),
 (38.93, 42.89, "Application deploy chesina tarvata kuda DevOps Engineer pani complete kaadu!"),
 (43.35, 47.76, "Application sarigga run avuthunda, errors emaina vasthunnaya ani monitor chestadu."),
 (48.14, 54.56, "So, DevOps Engineer ante automation, deployment, cloud infrastructure, monitoring meeda work chese engineer."),
 (54.86, 55.96, "Idi Day 2!"),
 (56.26, 59.89, "Repu Day 3 lo DevOps Lifecycle ni step by step telusukundam."),
 (60.20, 60.95, "Follow avvandi!"),
]
# short pauses inside sentences (end time = start of the next phrase), used to snap word times
PAUSE_ENDS = [1.127, 4.380, 9.970, 12.872, 13.886, 15.661, 18.952, 21.560, 24.460, 25.351, 25.774, 29.917,
              31.294, 31.498, 33.008, 33.880, 37.786, 42.156, 45.349, 48.677, 50.103, 51.765, 52.931, 58.755]
# scene boundaries = the paragraph pauses in the audio
BOUNDS = [0, 8.41, 17.49, 29.23, 38.49, 47.76, DUR]

def _tok(s): return s.split()
def _clean(w): return "".join(ch for ch in w.lower() if ch.isalnum())

def _word_times(i):
    a, b, text = SENT[i]
    toks = _tok(text)
    wts = [len(_clean(w)) + 1 for w in toks]
    tot = sum(wts)
    cum = [sum(wts[:k]) for k in range(len(toks))]
    est = [a + (b - a) * c / tot for c in cum]
    # anchor each mid-sentence pause to the nearest word start (one word per pause, increasing order)
    anchors = {0: a}
    for pe in PAUSE_ENDS:
        if a + .3 < pe < b - .3:
            k = min(range(1, len(toks)), key=lambda j: abs(est[j] - pe))
            if abs(est[k] - pe) < .6 and k not in anchors and all((k - j) * (pe - anchors[j]) > 0 or True for j in anchors):
                anchors[k] = pe
    ks = sorted(anchors)
    # drop anchors that break monotonic time order or leave <0.15s per word
    good = [ks[0]]
    for k in ks[1:]:
        if anchors[k] - anchors[good[-1]] >= .15 * (k - good[-1]): good.append(k)
    out = [0.0] * len(toks)
    for gi, k0 in enumerate(good):
        k1 = good[gi + 1] if gi + 1 < len(good) else len(toks)
        t0 = anchors[k0]; t1 = anchors[good[gi + 1]] if gi + 1 < len(good) else b
        seg = sum(wts[k0:k1])
        for k in range(k0, k1):
            out[k] = t0 + (t1 - t0) * sum(wts[k0:k]) / seg
    return toks, out
WORDS = [_word_times(i) for i in range(len(SENT))]

def wt(sent, word, occ=0):
    """Absolute audio time at which `word` starts in sentence number `sent` (1-based)."""
    toks, times = WORDS[sent - 1]
    k = _clean(word); n = 0
    for tk, tm in zip(toks, times):
        if _clean(tk).startswith(k):
            if n == occ: return tm
            n += 1
    raise KeyError((sent, word))

CAPS = [  # (sentence number, caption chunks); chunks must concatenate to the sentence
 (1, ["Day 1 lo DevOps ante enti telusukunnam kada!"]),
 (2, ["Mari aa process ni real ga implement chese", "DevOps Engineer em chestadu?"]),
 (3, ["DevOps Engineer main ga developers create chesina application ni", "testing nunchi deployment varaku", "smooth ga, automatic ga run ayyela help chestadu."]),
 (4, ["Example ki, developer code ni GitHub lo push chesinappudu,", "DevOps Engineer setup chesina CI/CD pipeline", "automatic ga code ni test chesi, build chesi,", "deployment process ni easy chestundi."]),
 (5, ["Dinikosam Git, Jenkins, Docker,", "Kubernetes, AWS laanti tools use chestaru."]),
 (6, ["Prathi tool ki oka specific purpose untundi."]),
 (7, ["Application deploy chesina tarvata kuda", "DevOps Engineer pani complete kaadu!"]),
 (8, ["Application sarigga run avuthunda,", "errors emaina vasthunnaya ani monitor chestadu."]),
 (9, ["So, DevOps Engineer ante automation, deployment,", "cloud infrastructure, monitoring meeda work chese engineer."]),
 (10, ["Idi Day 2!"]),
 (11, ["Repu Day 3 lo DevOps Lifecycle ni step by step telusukundam."]),
 (12, ["Follow avvandi!"]),
]
CAP_EVENTS = []  # (start, end, text)
for si, chunks in CAPS:
    toks, times = WORDS[si - 1]
    assert sum(len(_tok(c)) for c in chunks) == len(toks), si
    k = 0
    for ci, c in enumerate(chunks):
        st = times[k]; k += len(_tok(c))
        en = times[k] if k < len(toks) else SENT[si - 1][1] + .15
        CAP_EVENTS.append((st - .05, en, c))

def pop(t, cue, dur=.5): return ease((t - cue) / dur)

def s_hook(d, t):
    p = ease(t / .8)
    ctext(d, (W / 2, 520 - (1 - p) * 120), "DAY 2", F(210), mix(BG1, CY, p))
    ctext(d, (W / 2, 720), "100 Days of DevOps", F(52), mix(BG1, YE, pop(t, .5, .6)))
    q = pop(t, wt(2, "DevOps"))
    rbox(d, [140, 860, 940, 1000], mix(BG1, WH, .08 * q), mix(BG1, CY, q), 40, 4)
    ctext(d, (W / 2, 930), "DevOps Engineer", F(72), mix(BG1, WH, q))
    ctext(d, (W / 2, 1110), "em chestadu?", F(100), mix(BG1, OR, pop(t, wt(2, "em"), .6)))
    node(d, 330, 1360, "Day 1", GY, pop(t, wt(1, "Day")), "DevOps ante?", 230)
    arrow(d, 450, 1360, 630, 1360, CY, pop(t, wt(2, "Mari"), .6))
    node(d, 750, 1360, "Day 2", CY, pop(t, wt(2, "process")), "Role", 230)

def s_role(d, t):
    title(d, "DevOps Engineer", "Bridge: Dev  ->  Production", 8.5, t)
    y = 800
    node(d, 540, y, "DevOps", CY, pop(t, wt(3, "DevOps")), "Engineer", 240)
    node(d, 190, y, "Dev", PK, pop(t, wt(3, "developers")), "code")
    arrow(d, 290, y, 410, y, CY, pop(t, wt(3, "create"), .6))
    node(d, 890, y, "Prod", GR, pop(t, wt(3, "varaku")), "users")
    arrow(d, 670, y, 790, y, CY, pop(t, wt(3, "varaku") + .2, .6))
    for i, (s, cue) in enumerate([("Testing", "testing"), ("Build", "nunchi"), ("Deploy", "deployment")]):
        p = pop(t, wt(3, cue))
        x = 190 + i * 350
        rbox(d, [x - 140, 1130, x + 140, 1250], mix(BG1, OR, .25 * p), mix(BG1, OR, p), 28)
        ctext(d, (x, 1190), s, F(44), mix(BG1, WH, p))
    ctext(d, (W / 2, 1400), "smooth + automatic", F(60), mix(BG1, YE, pop(t, wt(3, "smooth"), .6)))

def s_pipeline(d, t):
    title(d, "CI/CD Pipeline", "Push  ->  Test  ->  Build  ->  Deploy", wt(4, "CI/CD") - .3, t)
    stages = [("GitHub", PK, "GitHub", "push"), ("Test", YE, "test", "test"), ("Build", OR, "build", "build"), ("Deploy", GR, "deployment", "deployment")]
    ys = [600, 850, 1100, 1350]
    for i, (n, c, cue, _) in enumerate(stages):
        a = wt(4, cue) if i else wt(4, "push") - .6
        if i == 0: a = wt(4, "GitHub")
        p = pop(t, a)
        node(d, 330, ys[i], n, c, p, None, 190)
        fill_start = wt(4, "push") if i == 0 else a
        done = ease((t - fill_start) / 1.0)
        bx = 480
        rbox(d, [bx, ys[i] - 22, bx + 480, ys[i] + 22], mix(BG1, WH, .08 * p), None, 22)
        if p > 0:
            rbox(d, [bx, ys[i] - 22, bx + max(1, 480 * done), ys[i] + 22], c, None, 22)
        if done >= 1:
            ctext(d, (bx + 440, ys[i] + 62), "OK", F(34), GR)
        if i > 0:
            arrow(d, 330, ys[i - 1] + 95, 330, ys[i] - 95, stages[i - 1][1], pop(t, a - .35, .35))
    ctext(d, (W / 2, 1530), "Sab automatic!", F(58), mix(BG1, YE, pop(t, wt(4, "easy"), .5)))

def s_tools(d, t):
    sub_t = wt(6, "Prathi")
    ctext(d, (W / 2, 250), "DevOps Tools", F(78), mix(BG1, WH, pop(t, 29.3, .6)))
    ctext(d, (W / 2, 335), "Prathi tool ki oka purpose", F(38, False), mix(BG1, CY, pop(t, sub_t, .6)))
    tools = [("Git", "Version control", PK, "Git"), ("Jenkins", "CI/CD automation", OR, "Jenkins"), ("Docker", "Containers", CY, "Docker"),
             ("Kubernetes", "Orchestration", (90, 140, 255), "Kubernetes"), ("AWS", "Cloud", YE, "AWS")]
    for i, (n, sub, c, cue) in enumerate(tools):
        p = pop(t, wt(5, cue))
        y = 560 + i * 225
        x = lerp(W + 400, 0, p)
        glow = max(0, 1 - abs(t - (sub_t + .25 + i * .35)) / .35) if t > sub_t else 0
        rbox(d, [110 + x, y - 90, 970 + x, y + 90], mix(BG1, c, .2 + .25 * glow), c, 34, 5 + int(4 * glow))
        d.ellipse([150 + x, y - 55, 260 + x, y + 55], fill=c)
        ctext(d, (205 + x, y), n[0], F(60), BG1)
        ctext(d, (300 + x, y - 24), n, F(54), WH, "lm")
        ctext(d, (300 + x, y + 36), sub, F(32, False), mix(BG1, c, pop(t, sub_t, .6)), "lm")

def s_monitor(d, t):
    title(d, "Monitoring", "Deploy tarvata kuda pani untundi", 38.6, t)
    rbox(d, [90, 520, 990, 1150], mix(BG1, WH, .05), CY, 36)
    for k in range(1, 5):
        d.line([130, 520 + k * 126, 950, 520 + k * 126], fill=mix(BG1, WH, .12), width=2)
    ts, te = wt(7, "tarvata"), 47.6
    te_err, t_mon = wt(8, "errors"), wt(8, "monitor")
    i_sp = 60 * (te_err + .5 - ts) / (te - ts)
    pts = []
    for i in range(60):
        v = 0.5 + .12 * math.sin(i * .5) + .05 * math.sin(i * 1.7) + .35 * math.exp(-((i - i_sp) ** 2) / 4)
        pts.append((140 + i * 13.5, 1100 - v * 520))
    n = int(len(pts) * max(0, min(1, (t - ts) / (te - ts))))
    for a, b in zip(pts[:max(0, n - 1)], pts[1:n]):
        d.line([a, b], fill=PK if b[1] < 800 else GR, width=7)
    bad = te_err <= t < t_mon + .9
    pills = [("Server", GR, wt(8, "sarigga")), ("Errors", PK if bad else GR, te_err), ("Logs", GR, t_mon)]
    for i, (s, c, cue) in enumerate(pills):
        p = pop(t, cue, .4)
        x = 200 + i * 340
        rbox(d, [x - 140, 1230, x + 140, 1330], mix(BG1, c, .25 * p), mix(BG1, c, p) if p > 0 else mix(BG1, WH, .15), 30)
        d.ellipse([x - 110, 1268, x - 86, 1292], fill=mix(BG1, c, p) if p > 0 else GY)
        ctext(d, (x + 15, 1280), s, F(38), WH)
    if bad and t < t_mon:
        a = .5 + .5 * math.sin(t * 9)
        ctext(d, (W / 2, 1450), "ALERT! Error detected", F(54), mix(BG1, PK, .5 + .5 * a))
    elif t >= t_mon:
        ctext(d, (W / 2, 1450), "Monitoring ON - sab healthy", F(54), GR)

def s_recap(d, t):
    ctext(d, (W / 2, 250), "DevOps Engineer =", F(70), mix(BG1, WH, pop(t, wt(9, "So"), .5)))
    for i, (s, c, cue) in enumerate([("Automation", CY, "automation"), ("Deployment", OR, "deployment"), ("Cloud Infra", YE, "cloud"), ("Monitoring", GR, "monitoring")]):
        p = pop(t, wt(9, cue))
        y = 440 + i * 170
        rbox(d, [140 + (1 - p) * 900, y - 70, 940 + (1 - p) * 900, y + 70], mix(BG1, c, .22), c, 34)
        ctext(d, (W / 2 + (1 - p) * 900, y), s, F(62), WH)
    ctext(d, (W / 2, 1090), "Idi Day 2!", F(70), mix(BG1, YE, pop(t, wt(10, "Idi"), .4)))
    ctext(d, (W / 2, 1410), "Day 3: DevOps Lifecycle", F(58), mix(BG1, YE, pop(t, wt(11, "Repu"), .5)))
    ctext(d, (W / 2, 1490), "repu!", F(48, False), mix(BG1, CY, pop(t, wt(11, "Repu") + .3, .5)))
    p = pop(t, wt(11, "Lifecycle"), .5)
    hit = pop(t, wt(12, "Follow"), .25)
    w = 400 * (1 + .12 * hit * (1 if t < 60.7 else 0) + .02 * math.sin(t * 6))
    rbox(d, [W / 2 - w, 1190, W / 2 + w, 1320], mix(BG1, PK, p), None, 60)
    ctext(d, (W / 2, 1255), "FOLLOW", F(72), mix(BG1, WH, p))

RENDER = [s_hook, s_role, s_pipeline, s_tools, s_monitor, s_recap]

def caption(d, t):
    for a, b, c in CAP_EVENTS:
        if a <= t < b:
            words, ln, out = c.split(), "", []
            for w_ in words:
                if len(ln) + len(w_) > 30: out.append(ln); ln = w_
                else: ln = (ln + " " + w_).strip()
            out.append(ln)
            h = 70 * len(out) + 40
            top = 1790 - h
            rbox(d, [50, top, 1030, 1830], (0, 0, 0), None, 30)
            for k, o in enumerate(out):
                ctext(d, (W / 2, top + 55 + k * 70), o, F(46), WH)
            return

def frame(fi):
    t = fi / FPS
    im, d = bg(t)
    for k in range(len(RENDER)):
        a, b = BOUNDS[k], BOUNDS[k + 1]
        if a <= t < b:
            RENDER[k](d, t)
            if t - a < .2 or b - t < .2:
                f = min(t - a, b - t) / .2
                im = Image.blend(Image.new("RGB", (W, H), BG1), im, max(0, f))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W * t / DUR, 12], fill=CY)
    ctext(d, (W / 2, 70), "100 DAYS OF DEVOPS", F(30), GY)
    caption(d, t)
    return im

def main(audio, out):
    n = int(math.ceil(DUR * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
