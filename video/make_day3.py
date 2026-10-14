"""Day 3 (DevOps Lifecycle) video, 1080x1920, black / neon-green palette, synced to a voiceover.
Usage: python3 make_day3.py voiceover.mp3 out.mp4   (needs Pillow, ffmpeg)

Sync: sentence windows in SENT were read off the voiceover's pauses (ffmpeg silencedetect).
Inside a sentence, the detected short pauses split it into speech segments; words are spread
over those segments by letter count, so every cue/caption is keyed to a word via wt().
"""
import math, re, subprocess, sys
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

# ---------------- audio sync data ----------------
SENT = [
 (0.05, 2.91,  "Day 2 lo DevOps Engineer em chestado telusukunnam kada!"),
 (3.67, 7.94,  "Mari oka application idea nunchi users daggariki ela reach avuthundi?"),
 (8.40, 9.96,  "Ade DevOps Lifecycle!"),
 (10.52, 11.76, "First step Plan!"),
 (12.31, 15.83, "Team application lo em features undalo decide chestundi."),
 (16.27, 17.54, "Next Code!"),
 (18.03, 20.79, "Developers application ki kavalsina code write chestaru."),
 (21.25, 22.49, "Next Build!"),
 (22.86, 25.09, "Code ni application ga ready chestaru."),
 (25.49, 26.73, "Tarvata Test!"),
 (27.11, 36.87, "Application lo bugs unnaya, correct ga work avuthunda ani automatic ga test chestaru."),
 (37.26, 38.55, "Next Release!"),
 (38.88, 43.20, "Tested application ni release ki prepare chestaru."),
 (43.54, 52.59, "Deploy ante application ni server or cloud lo install chesi users ki available ga chestaru."),
 (52.96, 56.73, "Application deploy chesaka Operate stage lo application ni run chestaru."),
 (57.02, 61.49, "Monitor stage lo performance, errors, server health ni continuously check chestaru."),
 (61.77, 67.55, "Monitoring lo problem kanipisthe, team feedback teesukoni improvements chestundi."),
 (67.93, 71.40, "Ila ee cycle malli repeat avuthundi!"),
 (71.74, 74.76, "Idi DevOps Lifecycle!"),
 (75.12, 79.12, "Day 4 lo Traditional IT ki DevOps ki madhya difference telusukundam."),
 (79.46, 80.43, "Follow avvandi!"),
]
CAPS = {
 1: ["Day 2 lo DevOps Engineer em chestado telusukunnam kada!"],
 2: ["Mari oka application idea nunchi", "users daggariki ela reach avuthundi?"],
 3: ["Ade DevOps Lifecycle!"], 4: ["First step Plan!"],
 5: ["Team application lo em features", "undalo decide chestundi."],
 6: ["Next Code!"], 7: ["Developers application ki kavalsina", "code write chestaru."],
 8: ["Next Build!"], 9: ["Code ni application ga ready chestaru."], 10: ["Tarvata Test!"],
 11: ["Application lo bugs unnaya,", "correct ga work avuthunda ani", "automatic ga test chestaru."],
 12: ["Next Release!"], 13: ["Tested application ni", "release ki prepare chestaru."],
 14: ["Deploy ante application ni", "server or cloud lo install chesi", "users ki available ga chestaru."],
 15: ["Application deploy chesaka", "Operate stage lo application ni run chestaru."],
 16: ["Monitor stage lo performance,", "errors, server health ni", "continuously check chestaru."],
 17: ["Monitoring lo problem kanipisthe,", "team feedback teesukoni", "improvements chestundi."],
 18: ["Ila ee cycle", "malli repeat avuthundi!"], 19: ["Idi DevOps Lifecycle!"],
 20: ["Day 4 lo Traditional IT ki", "DevOps ki madhya difference", "telusukundam."],
 21: ["Follow avvandi!"],
}

def detect_silences(audio):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af", "silencedetect=noise=-32dB:d=0.1", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    return list(zip(st, en))

def _clean(w): return "".join(ch for ch in w.lower() if ch.isalnum())

# tokens per speech segment where the pause pattern clearly shows the phrasing (overrides the automatic split)
GROUPS = {11: [4, 3, 2, 2, 1, 1], 14: [1, 3, 1, 4, 3, 2, 1], 17: [1, 2, 1, 1, 1, 1, 1, 1]}

def word_times(a, b, text, sil, groups=None):
    toks = text.split()
    wts = [len(_clean(w)) + 1 for w in toks]
    tot = sum(wts)
    cuts = [a] + [x for s, e in sil if a + .1 < s and e < b - .1 and e - s >= .18 for x in (s, e)] + [b]
    segs = [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts) - 1, 2)]
    if groups and len(groups) == len(segs) and sum(groups) == len(toks):
        out, k = [0.0] * len(toks), 0
        for (s, e), g in zip(segs, groups):
            seg = sum(wts[k:k + g])
            for j in range(k, k + g): out[j] = s + (e - s) * sum(wts[k:j]) / seg
            k += g
        return toks, out
    T = sum(e - s for s, e in segs)
    bounds, acc = [0], 0.0
    for s, e in segs[:-1]:
        acc += e - s
        k = min(range(1, len(toks)), key=lambda j: abs(sum(wts[:j]) / tot - acc / T)) if len(toks) > 1 else 1
        last = max(b_ for b_ in bounds if b_ is not None)
        bounds.append(k if last < k < len(toks) else None)
    # build groups: a boundary of None merges the segment with the next
    groups, cur_s, k0 = [], segs[0][0], 0
    for i, (s, e) in enumerate(segs):
        kb = bounds[i + 1] if i + 1 < len(segs) else len(toks)
        if kb is None: continue
        groups.append((k0, kb, cur_s, e))
        k0, cur_s = kb, (segs[i + 1][0] if i + 1 < len(segs) else e)
    out = [0.0] * len(toks)
    for k0, k1, s, e in groups:
        seg = sum(wts[k0:k1])
        for k in range(k0, k1): out[k] = s + (e - s) * sum(wts[k0:k]) / seg
    return toks, out

WORDS = []
def init_sync(audio):
    sil = detect_silences(audio)
    WORDS[:] = [word_times(a, b, t, sil, GROUPS.get(i + 1)) for i, (a, b, t) in enumerate(SENT)]

def wt(sent, word, occ=0):
    toks, times = WORDS[sent - 1]
    k, n = _clean(word), 0
    for tk, tm in zip(toks, times):
        if _clean(tk).startswith(k):
            if n == occ: return tm
            n += 1
    raise KeyError((sent, word))

def caption_events():
    ev = []
    for si, chunks in CAPS.items():
        toks, times = WORDS[si - 1]
        assert sum(len(c.split()) for c in chunks) == len(toks), si
        k = 0
        for c in chunks:
            st = times[k]; k += len(c.split())
            en = times[k] if k < len(toks) else SENT[si - 1][1] + .2
            ev.append((st - .05, en, c))
    return ev

# ---------------- visuals ----------------
STAGES = [("PLAN", "Features decide chestaru", 4, "Plan"), ("CODE", "Developers code write", 6, "Code"),
          ("BUILD", "Code → application", 8, "Build"), ("TEST", "Automatic bug checks", 10, "Test"),
          ("RELEASE", "Tested app ready", 12, "Release"), ("DEPLOY", "Server / Cloud → users", 14, "Deploy"),
          ("OPERATE", "Application run avuthundi", 15, "Operate"), ("MONITOR", "Performance - errors - health", 16, "Monitor")]
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

def draw_intro(d, t, al):
    c = lambda col: mix(BG, col, al)
    # S1: recap chip
    p = pop(t, wt(1, "Day"))
    rbox(d, [300, 560, 780, 700], mix(BG, GREEN, .12 * p * al), c(GREEN) if p else BG, 40)
    ctext(d, (540, 630), "DAY 2  ✓", F(80), c(mix(BG, GREEN, p)))
    ctext(d, (540, 800), "DevOps Engineer", F(70), c(mix(BG, WHITE, pop(t, wt(1, "DevOps")))))
    # S2: idea -> users
    pi, pu, pq = pop(t, wt(2, "oka")), pop(t, wt(2, "users")), pop(t, wt(2, "ela"), .3)
    for cx, lab, p_ in [(250, "IDEA", pi), (830, "USERS", pu)]:
        rbox(d, [cx - 150, 1090, cx + 150, 1210], mix(BG, GREEN, .1 * p_ * al), c(mix(BG, GREEN, p_)), 36)
        ctext(d, (cx, 1150), lab, F(56), c(mix(BG, WHITE, p_)))
    if pq:
        for k in range(7):
            x = 430 + k * 33 + (t * 40) % 33
            if x < 650: d.ellipse([x - 6, 1144, x + 6, 1156], fill=c(mix(BG, GREEN, pq * .7)))
        ctext(d, (540, 1060), "?", F(90), c(mix(BG, GREEN, pq)))

def stage_cues():
    return [wt(s, w) for _, _, s, w in STAGES]

def draw_ring(d, t, al, cues):
    c = lambda col: mix(BG, col, al)
    t_ade, t_fb, t_ila, t_idi = wt(3, "Ade"), wt(17, "feedback"), wt(18, "Ila"), wt(19, "Idi")
    # title
    ctext(d, (540, 250), "DEVOPS LIFECYCLE", F(68), c(mix(BG, WHITE, pop(t, wt(3, "DevOps"), .5))))
    # ring track
    box = [CX - R, CY_ - R, CX + R, CY_ + R]
    ring_p = pop(t, t_ade, .8)
    d.ellipse(box, outline=c(mix(BG, DIM, ring_p)), width=8)
    # progress arc to the latest active stage (animated)
    cur = max([i for i, ct in enumerate(cues) if t >= ct], default=-1)
    if cur >= 0:
        prev_a = ANG[cur - 1] if cur > 0 else ANG[0]
        a_end = lerp(prev_a, ANG[cur], ease((t - cues[cur]) / .7)) if cur > 0 else ANG[0]
        if a_end > -90: d.arc(box, -90, a_end, fill=c(GREEN), width=12)
    # feedback arc Monitor -> Plan
    if t >= t_fb:
        fp = ease((t - t_fb) / 1.6)
        d.arc(box, 225, 225 + 45 * fp, fill=c(WHITE), width=12)
        if fp > .9:
            x, y = pos(0)
            d.polygon([(x - 18, y - 30), (x + 22, y), (x - 18, y + 30)], fill=c(WHITE))
    # pills
    for i, (name, _, _, _) in enumerate(STAGES):
        x, y = pos(i)
        stag = ease((t - t_ade - .15 * i) / .4)
        active = (cues[i] <= t) and (i == cur) and t < t_fb
        done = cues[i] <= t and not active
        sc = 1 + (.12 * (1 - ease((t - cues[i]) / .4)) if cues[i] <= t else 0)
        pw, ph = 100 * sc, 44 * sc
        if active:
            rbox(d, [x - pw, y - ph, x + pw, y + ph], c(GREEN), None, 30)
            ctext(d, (x, y), name, F(int(34 * sc)), c(BG))
        else:
            col = GREEN if done else DIM
            rbox(d, [x - pw, y - ph, x + pw, y + ph], c(BG), c(mix(BG, col, stag)), 30, 4)
            ctext(d, (x, y), name, F(34), c(mix(BG, WHITE if done else GREY, stag)))
    # centre text
    idx = cur
    if t >= t_idi:
        ctext(d, (CX, CY_ - 40), "∞", F(150), c(GREEN)); ctext(d, (CX, CY_ + 70), "DevOps Lifecycle", F(44), c(WHITE))
    elif t >= t_ila:
        pu = 1 + .05 * math.sin(t * 7)
        ctext(d, (CX, CY_ - 40), "REPEAT", F(int(92 * pu)), c(GREEN)); ctext(d, (CX, CY_ + 70), "cycle malli repeat avuthundi", F(34), c(WHITE))
    elif t >= t_fb:
        ctext(d, (CX, CY_ - 40), "FEEDBACK", F(84), c(WHITE)); ctext(d, (CX, CY_ + 70), "problem → improvements", F(36), c(GREEN))
    elif idx >= 0:
        n, desc = STAGES[idx][0], STAGES[idx][1]
        p = ease((t - cues[idx]) / .35)
        ctext(d, (CX, CY_ - 120), f"{idx + 1:02d} / 08", M(40), c(mix(BG, GREY, p)))
        ctext(d, (CX, CY_ - 30), n, F(100 if len(n) < 7 else 84), c(mix(BG, GREEN, p)))
        ctext(d, (CX, CY_ + 70), desc, F(36), c(mix(BG, WHITE, p)))
    elif ring_p:
        ctext(d, (CX, CY_), "∞", F(140), c(mix(BG, GREEN, ring_p)))

def draw_outro(d, t, al):
    c = lambda col: mix(BG, col, al)
    p = pop(t, wt(20, "Day"), .5)
    ctext(d, (540, 700), "DAY 4", F(220), c(mix(BG, WHITE, p)))
    ctext(d, (540, 900), "Traditional IT", F(80), c(mix(BG, WHITE, pop(t, wt(20, "Traditional")))))
    ctext(d, (540, 1000), "vs", F(50), c(mix(BG, GREY, pop(t, wt(20, "DevOps")))))
    ctext(d, (540, 1110), "DevOps", F(110), c(mix(BG, GREEN, pop(t, wt(20, "DevOps")))))
    pf = pop(t, wt(20, "difference"), .5)
    hit = pop(t, wt(21, "Follow"), .25)
    w = 300 * (1 + .1 * hit + .02 * math.sin(t * 6))
    rbox(d, [540 - w, 1260, 540 + w, 1380], mix(BG, GREEN, pf * al), None, 60)
    ctext(d, (540, 1320), "FOLLOW", M(64), c(mix(BG, BG if False else (0, 0, 0), 1) if pf > .5 else BG))

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

def main(audio, out):
    init_sync(audio)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                               capture_output=True, text=True).stdout)
    events, cues = caption_events(), stage_cues()
    t_ring_in, t_out = wt(3, "Ade"), wt(20, "Day")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
    for fi in range(int(math.ceil(dur * FPS))):
        t = fi / FPS
        im = background(); d = ImageDraw.Draw(im)
        if t < t_ring_in + .1: draw_intro(d, t, 1 - ease((t - (t_ring_in - .15)) / .3))
        if t_ring_in - .2 <= t < t_out + .3: draw_ring(d, t, min(ease((t - (t_ring_in - .2)) / .3), 1 - ease((t - (t_out - .1)) / .4)), cues)
        if t >= t_out - .1: draw_outro(d, t, ease((t - (t_out + .3)) / .4))
        d.rectangle([0, 0, W * t / dur, 12], fill=GREEN)
        ctext(d, (W / 2, 70), "100 DAYS OF DEVOPS", M(30), GREY)
        caption(d, t, events)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
