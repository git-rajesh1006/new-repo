"""Day 3 (DevOps Lifecycle) video, 1080x1920, black / neon-green palette, synced to a voiceover.
Usage: python3 make_day3.py voiceover.mp3 day3-sync.json out.mp4   (needs Pillow, ffmpeg)

Sync: day3-sync.json (made by align_voiceover.py) holds per-word start times from forced alignment of
the script against the voiceover, phrase by phrase inside windows measured from the audio's pauses.
Every visual cue and caption is keyed to a spoken word via wt().
"""
import json, math, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FD = "/usr/share/fonts/truetype/dejavu/"
@lru_cache(None)
def F(sz): return ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", sz)
@lru_cache(None)
def M(sz): return ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", sz)

BG, GRID, GREEN, WHITE, GREY, DIM = (10, 10, 10), (20, 20, 20), (0, 255, 160), (255, 255, 255), (110, 110, 110), (45, 45, 45)
def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def pop(t, cue, dur=.45): return ease((t - cue) / dur)


RED = (255, 95, 95)
PH = []   # phrases: dict(a, b, text, times)
def load_sync(path): PH[:] = json.load(open(path))

def wt(key, word=None, occ=0):
    """Start time of `word` in the phrase whose text is `key` (exact match first, else prefix match)."""
    p = next((q for q in PH if q["text"] == key), None) or next(q for q in PH if q["text"].startswith(key))
    if word is None: return p["times"][0]
    toks, n = p["text"].split(), 0
    for tk, tm in zip(toks, p["times"]):
        if "".join(ch for ch in tk.lower() if ch.isalnum()).startswith("".join(ch for ch in word.lower() if ch.isalnum())):
            if n == occ: return tm
            n += 1
    raise KeyError((key, word))

CAPS = {
 "Day two lo DevOps Engineer em chestado telusukunnam kada!": ["Day two lo DevOps Engineer", "em chestado telusukunnam kada!"],
 "oka application idea nunchi users daggariki ela reach avuthundi?": ["oka application idea nunchi", "users daggariki ela reach avuthundi?"],
 "team application lo em features undalo decide chestundi.": ["team application lo em features", "undalo decide chestundi."],
 "Developers application ki kavalsina code write chestaru.": ["Developers application ki", "kavalsina code write chestaru."],
 "Code ni complete application ga ready chestaru.": ["Code ni complete application", "ga ready chestaru."],
 "Application ni release cheyadaniki prepare chestaru.": ["Application ni release", "cheyadaniki prepare chestaru."],
 "Application ni server or cloud lo deploy chesi users ki available ga chestaru.": ["Application ni server or cloud", "lo deploy chesi users ki", "available ga chestaru."],
 "Ee cycle repeat avuthu software ni continuously improve chestundi.": ["Ee cycle repeat avuthu", "software ni continuously improve chestundi."],
 "Idi mana 100 Days of DevOps series lo Day 3!": ["Idi mana 100 Days of DevOps", "series lo Day 3!"],
 "Repu Day four lo Traditional IT ki DevOps ki madhya difference telusukundam.": ["Repu Day four lo", "Traditional IT ki DevOps", "ki madhya difference telusukundam."],
}

def caption_events():
    ev = []
    for i, p in enumerate(PH):
        chunks, toks, k = CAPS.get(p["text"], [p["text"]]), p["text"].split(), 0
        assert sum(len(c.split()) for c in chunks) == len(toks), p["text"]
        for ci, c in enumerate(chunks):
            st = p["times"][k]; k += len(c.split())
            en = p["times"][k] if k < len(toks) else p["b"] + .15
            if k >= len(toks) and i + 1 < len(PH) and PH[i + 1]["a"] - p["b"] < .5: en = PH[i + 1]["times"][0]   # no flicker over short gaps
            ev.append((st - .04, en, c))
    return ev

# ---------------- visuals ----------------
NAMES = ["PLAN", "CODE", "BUILD", "TEST", "RELEASE", "DEPLOY", "OPERATE", "MONITOR"]
CX, CY_, R = 540, 940, 370
ANG = [-90 + i * 45 for i in range(8)]
def ctext(d, xy, s, font, fill, anchor="mm"): d.text(xy, s, font=font, fill=fill, anchor=anchor)
def rbox(d, box, fill, outline=None, r=36, w=4): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=w)
def pos(i, r=R): a = math.radians(ANG[i]); return CX + r * math.cos(a), CY_ + r * math.sin(a)

_bg = None
def background():
    global _bg
    if _bg is None:
        _bg = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(_bg)
        for x in range(0, W, 90): d.line([x, 0, x, H], fill=GRID)
        for y in range(0, H, 90): d.line([0, y, W, y], fill=GRID)
    return _bg.copy()

class Cues: pass
def make_cues():
    q = Cues()
    q.ade = wt("Ade DevOps", "Ade")
    q.p1 = [wt("PLAN!"), wt("CODE!"), wt("BUILD!"), wt("TEST!"), wt("RELEASE!"), wt("DEPLOY!"), wt("OPERATE and", "OPERATE"), wt("OPERATE and", "MONITOR")]
    q.rec = [wt(n.capitalize() + ("!" if n == "MONITOR" else ",")) for n in NAMES]
    q.wait, q.prob, q.fb, q.impr = wt("But wait"), wt("Oka problem"), wt("team feedback", "feedback"), wt("team feedback", "improvements")
    q.rep, q.idi, q.repu = wt("Ee cycle"), wt("Idi mana"), wt("Repu Day")
    S = [(q.ade, "", "∞", "DevOps Lifecycle", GREEN)]
    subs = ["Features decide chestundi", "Developers code write chestaru", "Complete application ready",
            "Automatic bug checks", "Prepare tested application", "Server / Cloud → users",
            "Application run avuthundi", "Performance • Errors • Health"]
    for i in range(8): S.append((q.p1[i], f"{i + 1:02d} / 08", NAMES[i], subs[i], GREEN))
    S += [(wt("Application correct"), "04 / 08", "TEST", "Works correctly?", GREEN), (wt("Bugs emaina"), "04 / 08", "TEST", "Any bugs?", GREEN),
          (wt("Ani automatic"), "04 / 08", "TEST", "Automatic testing", GREEN), (wt("Tests pass"), "04 / 08", "TEST", "Tests pass ✓", GREEN),
          (q.wait, "", "BUT WAIT…", "mana pani ikkade aipodu!", WHITE),
          (wt("Application smooth"), "", "RUNNING?", "smooth ga run avuthunda?", GREEN), (wt("Performance ela"), "", "PERFORMANCE?", "ela undi?", GREEN),
          (wt("Errors emaina"), "", "ERRORS?", "emaina vasthunnaya?", GREEN), (wt("Veetannitini"), "08 / 08", "MONITOR", "continuously monitor chestaru", GREEN),
          (q.prob, "", "PROBLEM!", "kanipisthe…", RED), (q.fb, "", "FEEDBACK", "team feedback teesukoni", WHITE),
          (q.impr, "", "IMPROVE", "improvements chestundi", GREEN), (wt("And that's"), "", "∞", "beauty of DevOps", GREEN)]
    for i in range(8): S.append((q.rec[i], f"{i + 1:02d} / 08", NAMES[i], "", GREEN))
    S.append((q.rep, "", "REPEAT", "continuous improvement", GREEN))
    q.states = sorted(S, key=lambda x: x[0])
    return q

def draw_intro(d, t, al, q):
    c = lambda col: mix(BG, col, al)
    p = pop(t, wt("Day two", "Day"))
    rbox(d, [300, 560, 780, 700], mix(BG, GREEN, .12 * p * al), c(GREEN) if p else BG, 40)
    ctext(d, (540, 630), "DAY 2  ✓", F(80), c(mix(BG, GREEN, p)))
    ctext(d, (540, 800), "DevOps Engineer", F(70), c(mix(BG, WHITE, pop(t, wt("Day two", "DevOps")))))
    pi, pu, pq = pop(t, wt("oka application", "oka")), pop(t, wt("oka application", "users")), pop(t, wt("oka application", "ela"), .3)
    for cx, lab, p_ in [(250, "IDEA", pi), (830, "USERS", pu)]:
        rbox(d, [cx - 150, 1090, cx + 150, 1210], mix(BG, GREEN, .1 * p_ * al), c(mix(BG, GREEN, p_)), 36)
        ctext(d, (cx, 1150), lab, F(56), c(mix(BG, WHITE, p_)))
    if pq:
        for k in range(7):
            x = 430 + k * 33 + (t * 40) % 33
            if x < 650: d.ellipse([x - 6, 1144, x + 6, 1156], fill=c(mix(BG, GREEN, pq * .7)))
        ctext(d, (540, 1060), "?", F(90), c(mix(BG, GREEN, pq)))

def draw_ring(d, t, al, q):
    c = lambda col: mix(BG, col, al)
    ctext(d, (540, 250), "DEVOPS LIFECYCLE", F(68), c(mix(BG, WHITE, pop(t, wt("Ade DevOps", "DevOps"), .5))))
    box = [CX - R, CY_ - R, CX + R, CY_ + R]
    ring_p = pop(t, q.ade, .8)
    d.ellipse(box, outline=c(mix(BG, DIM, ring_p)), width=8)
    in_rec, after_rec = q.rec[0] <= t < q.rep, t >= q.rep
    # which pill is active, and how far the green arc reaches
    if t < q.prob:
        cur = max([i for i, ct in enumerate(q.p1) if t >= ct], default=-1); cues = q.p1
    elif in_rec:
        cur = max([i for i, ct in enumerate(q.rec) if t >= ct], default=-1); cues = q.rec
    else:
        cur = -1; cues = q.p1
    done_all = (q.prob <= t < q.rec[0]) or after_rec
    if after_rec: d.ellipse(box, outline=c(GREEN), width=12)
    elif done_all: d.arc(box, -90, 225, fill=c(GREEN), width=12)
    elif cur > 0:
        d.arc(box, -90, lerp(ANG[cur - 1], ANG[cur], ease((t - cues[cur]) / .7)), fill=c(GREEN), width=12)
    if q.fb <= t < q.rec[0]:
        fp = ease((t - q.fb) / 1.4)
        d.arc(box, 225, 225 + 45 * fp, fill=c(WHITE), width=12)
        if fp > .9:
            x, y = pos(0); d.polygon([(x - 18, y - 30), (x + 22, y), (x - 18, y + 30)], fill=c(WHITE))
    if after_rec:   # orbiting dot = the cycle repeating
        a = math.radians(-90 + 360 * (((t - q.rep) / 2.4) % 1))
        x, y = CX + R * math.cos(a), CY_ + R * math.sin(a)
        d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=c(WHITE))
    for i, name in enumerate(NAMES):
        x, y = pos(i)
        stag = ease((t - q.ade - .15 * i) / .4)
        active = i == cur and not done_all and not after_rec
        done = (cues[i] <= t and not active) if cur >= 0 else False
        if done_all or after_rec or (in_rec and not active): done = True
        hint = q.wait <= t < q.p1[6] and i >= 6     # "but wait…": the next stages beckon
        sc = 1 + (.12 * (1 - ease((t - cues[i]) / .4)) if active else 0)
        pw, ph = 100 * sc, 44 * sc
        if active:
            rbox(d, [x - pw, y - ph, x + pw, y + ph], c(GREEN), None, 30); ctext(d, (x, y), name, F(int(34 * sc)), c(BG))
        else:
            col = WHITE if hint and int(t * 4) % 2 == 0 else (GREEN if done else DIM)
            rbox(d, [x - pw, y - ph, x + pw, y + ph], c(BG), c(mix(BG, col, stag)), 30, 4)
            ctext(d, (x, y), name, F(34), c(mix(BG, WHITE if (done or hint) else GREY, stag)))
    st = [s for s in q.states if s[0] <= t]
    if st:
        ts, num, big, sub, col = st[-1]
        p = ease((t - ts) / .3)
        if num: ctext(d, (CX, CY_ - 120), num, M(40), c(mix(BG, GREY, p)))
        size = 100 if len(big) < 7 else 84 if len(big) < 9 else 64 if len(big) < 11 else 52
        if big == "∞": size = 150
        ctext(d, (CX, CY_ - (40 if not num else 30)), big, F(size), c(mix(BG, col, p)))
        if sub: ctext(d, (CX, CY_ + 70), sub, F(36), c(mix(BG, WHITE, p)))

def draw_card3(d, t, al, q):
    c = lambda col: mix(BG, col, al)
    ctext(d, (540, 760), "DAY 3  ✓", F(190), c(mix(BG, WHITE, pop(t, wt("Idi mana", "Day"), .5))))
    pb = pop(t, wt("Idi mana", "100"), .5)
    ctext(d, (540, 960), "100 DAYS OF DEVOPS", F(48), c(mix(BG, GREEN, pb)))
    rbox(d, [140, 1030, 940, 1070], c(mix(BG, DIM, pb)), None, 20)
    rbox(d, [140, 1030, 140 + 800 * .03 * ease((t - wt("Idi mana", "Day")) / 1.0) + 40, 1070], c(GREEN), None, 20) if pb else None
    ctext(d, (540, 1130), "3 / 100", M(44), c(mix(BG, GREY, pb)))

def draw_card4(d, t, al, q):
    c = lambda col: mix(BG, col, al)
    p = pop(t, wt("Repu Day", "Day"), .5)
    ctext(d, (540, 700), "DAY 4", F(220), c(mix(BG, WHITE, p)))
    ctext(d, (540, 900), "Traditional IT", F(80), c(mix(BG, WHITE, pop(t, wt("Repu Day", "Traditional")))))
    ctext(d, (540, 1000), "vs", F(50), c(mix(BG, GREY, pop(t, wt("Repu Day", "DevOps")))))
    ctext(d, (540, 1110), "DevOps", F(110), c(mix(BG, GREEN, pop(t, wt("Repu Day", "DevOps")))))
    pf = pop(t, wt("Repu Day", "difference"), .5)
    hit = pop(t, wt("Follow"), .25)
    w = 300 * (1 + .1 * hit + .02 * math.sin(t * 6))
    rbox(d, [540 - w, 1260, 540 + w, 1380], mix(BG, GREEN, pf * al), None, 60)
    ctext(d, (540, 1320), "FOLLOW", M(64), (0, 0, 0) if pf > .5 else BG)

def caption(d, t, events):
    for a, b, c in events:
        if a <= t < b:
            words, ln, out = c.split(), "", []
            for w_ in words:
                if len(ln) + len(w_) > 30: out.append(ln); ln = w_
                else: ln = (ln + " " + w_).strip()
            out.append(ln)
            h = 70 * len(out) + 40
            top = 1790 - h
            rbox(d, [50, top, 1030, 1830], (0, 0, 0), (40, 40, 40), 30, 3)
            for k, o in enumerate(out):
                ctext(d, (W / 2, top + 55 + k * 70), o, F(46), WHITE)
            return

def main(audio, sync, out):
    load_sync(sync)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                               capture_output=True, text=True).stdout)
    events, q = caption_events(), make_cues()
    ring_in, ring_out, card4_in = q.ade - .2, q.idi - .1, q.repu - .1
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
    for fi in range(int(math.ceil(dur * FPS))):
        t = fi / FPS
        im = background(); d = ImageDraw.Draw(im)
        fade = lambda a, b: ease((t - a) / .3) * (1 - ease((t - b) / .3))
        if t < q.ade + .1: draw_intro(d, t, 1 - ease((t - (q.ade - .15)) / .3), q)
        if ring_in <= t < ring_out + .4: draw_ring(d, t, fade(ring_in, ring_out), q)
        if ring_out <= t < card4_in + .4: draw_card3(d, t, fade(ring_out + .2, card4_in), q)
        if t >= card4_in: draw_card4(d, t, ease((t - (card4_in + .3)) / .3), q)
        d.rectangle([0, 0, W * t / dur, 12], fill=GREEN)
        ctext(d, (W / 2, 70), "100 DAYS OF DEVOPS", M(30), GREY)
        caption(d, t, events)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
