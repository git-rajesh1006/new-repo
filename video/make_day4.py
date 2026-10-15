"""Day 4 (Traditional IT vs DevOps) video, 1080x1920, black / neon-green palette, synced to a voiceover.
Usage: python3 make_day4.py voiceover.mp3 day4-sync.json out.mp4
day4-sync.json comes from: python3 align_voiceover.py day4_phrases voiceover.mp3 day4-sync.json
Every animation and caption is keyed to a spoken word via wt()."""
import json, math, subprocess, sys
from PIL import ImageDraw
from make_day3 import (F, M, W, H, FPS, BG, GREEN, WHITE, GREY, DIM, RED, ease, lerp, mix, pop,
                       ctext, rbox, background, caption)

PH = []
def clean(s): return "".join(ch for ch in s.lower() if ch.isalnum())
def wt(key, word=None, occ=0):
    p = next((q for q in PH if q["text"] == key), None) or next(q for q in PH if q["text"].startswith(key))
    if word is None: return p["times"][0]
    n = 0
    for tk, tm in zip(p["text"].split(), p["times"]):
        if clean(tk).startswith(clean(word)):
            if n == occ: return tm
            n += 1
    raise KeyError((key, word))

def caption_events():
    ev = []
    for i, p in enumerate(PH):
        toks = p["text"].split(); chunks, cur = [], []
        for k, tk in enumerate(toks):
            cur.append(tk)
            n = len(" ".join(cur))
            if k + 1 < len(toks) and (n + len(toks[k + 1]) > 50 or (tk[-1] in ",?!…" and n >= 22)):
                chunks.append(cur); cur = []
        chunks.append(cur)
        k = 0
        for ci, ch in enumerate(chunks):
            st = p["times"][k]; k += len(ch)
            en = p["times"][k] if k < len(toks) else p["b"] + .15
            if k >= len(toks) and i + 1 < len(PH) and PH[i + 1]["a"] - p["b"] < .5: en = PH[i + 1]["times"][0]
            ev.append((st - .04, en, " ".join(ch)))
    return ev

def pill(d, cx, cy, w, h, label, col, p, al, font=44, fill_p=0.0, r=30):
    c = lambda x: mix(BG, x, al)
    if p <= 0: return
    rbox(d, [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], c(mix(BG, col, .12 + .88 * fill_p)), c(mix(BG, col, p)), r, 4)
    ctext(d, (cx, cy), label, F(font), c(mix(BG if fill_p > .5 else mix(BG, WHITE, p), BG, fill_p) if fill_p > .5 else mix(BG, WHITE, p)))

def title(d, t, al, text, cue, col=WHITE, y=300, size=64):
    ctext(d, (540, y), text, F(size), mix(BG, mix(BG, col, pop(t, cue, .5)), al))

# ---------------- scenes ----------------
def sc_recap(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 760), "DAY 3  ✓", F(190), c(mix(BG, WHITE, pop(t, wt("Day 3", "Day"), .5))))
    ctext(d, (540, 940), "DevOps Lifecycle", F(70), c(mix(BG, GREEN, pop(t, wt("Day 3", "DevOps")))))

def sc_question(d, t, al):
    c = lambda x: mix(BG, x, al)
    k = "Traditional IT ki"
    pill(d, 540, 430, 520, 90, "INTERESTING QUESTION", GREEN, pop(t, wt("Mari oka"), .4), al, 36)
    ctext(d, (540, 650), "TRADITIONAL IT", F(92), c(mix(BG, WHITE, pop(t, wt(k, "Traditional")))))
    ctext(d, (540, 800), "VS", F(60), c(mix(BG, GREY, pop(t, wt(k, "ki")))))
    ctext(d, (540, 960), "DEVOPS", F(140), c(mix(BG, GREEN, pop(t, wt(k, "DevOps")))))
    q = pop(t, wt(k, "difference"), .4)
    ctext(d, (540, 1180), "DIFFERENCE?", F(90 + int(6 * math.sin(t * 6) * q)), c(mix(BG, WHITE, q)))

def sc_traditional(d, t, al):
    c = lambda x: mix(BG, x, al)
    k4, k5, k6 = "Traditional IT approach", "Tarvata", "Kaani deployment"
    title(d, t, al, "TRADITIONAL IT", wt(k4), GREY, 300, 60)
    pd_, po = pop(t, wt(k4, "Development")), pop(t, wt(k5, "Operations"))
    pill(d, 240, 800, 330, 150, "DEV TEAM", WHITE, pd_, al, 46)
    pill(d, 840, 800, 330, 150, "OPS TEAM", WHITE, po, al, 46)
    pw = pop(t, wt(k5), .5)                                   # the wall between the teams
    if pw: rbox(d, [520, 640, 560, 960], c(mix(BG, DIM, pw)), c(mix(BG, GREY, pw)), 10, 3)
    ctext(d, (540, 1010), "WALL", F(32), c(mix(BG, GREY, pw)))
    pa = pop(t, wt(k4, "application"))
    hand = ease((t - wt(k5, "handover")) / 1.3)
    if pa:
        x = lerp(240, 840, hand); y = 690 - 60 * math.sin(math.pi * hand)
        pill(d, x, y, 150, 70, "APP", GREEN, pa, al, 36, fill_p=1.0, r=24)
    pdp = pop(t, wt(k6, "deployment"))
    ctext(d, (540, 1110), "DEPLOYMENT", F(46), c(mix(BG, WHITE, pdp)))
    pe = pop(t, wt(k6, "errors"), .3)
    if pe: ctext(d, (840, 560), "ERROR ✕", F(60 + int(8 * math.sin(t * 9))), c(mix(BG, RED, pe)))
    pb = pop(t, wt(k6, "blame"), .3)
    if pb:
        ctext(d, (540, 1290), "BLAME GAME!", F(96), c(mix(BG, RED, pb)))
        for x0, x1 in ((420, 240), (660, 840)):
            d.line([x0, 930, x1, 930], fill=c(mix(BG, RED, pb)), width=6)

def bubble(d, box, lines, col, p, al, mark, mp):
    c = lambda x: mix(BG, x, al)
    if p <= 0: return
    rbox(d, box, c(mix(BG, col, .1 * p)), c(mix(BG, col, p)), 40, 4)
    for i, ln in enumerate(lines):
        ctext(d, ((box[0] + box[2]) / 2 - 40, (box[1] + box[3]) / 2 + (i - (len(lines) - 1) / 2) * 66), ln, F(48), c(mix(BG, WHITE, p)))
    ctext(d, (box[2] - 70, (box[1] + box[3]) / 2), mark, F(110), c(mix(BG, RED if mark == "✕" else GREEN, mp)))

def sc_blame(d, t, al):
    c = lambda x: mix(BG, x, al)
    title(d, t, al, "BLAME GAME", wt("Developers antaru"), RED, 300, 72)
    a = pop(t, wt("Developers antaru"), .4)
    if a: pill(d, 270, 470, 430, 70, "DEVELOPERS", GREEN, a, al, 36)
    bubble(d, [60, 540, 1020, 800], ["“Maa system lo", "application correct ga", "work avuthundi!”"], GREEN, pop(t, wt("“Maa")), al, "✓", pop(t, wt("“Maa", "avuthundi!”"), .3))
    b = pop(t, wt("Operations team antundi"), .4)
    if b: pill(d, 270, 960, 430, 70, "OPERATIONS", WHITE, b, al, 36)
    bubble(d, [60, 1030, 1020, 1290], ["“Production server lo", "application work", "avvatledu!”"], WHITE, pop(t, wt("“Production")), al, "✕", pop(t, wt("“Production", "avvatledu!”"), .3))

def check_row(d, y, label, p, al):
    c = lambda x: mix(BG, x, al)
    if p <= 0: return
    d.ellipse([110, y - 40, 190, y + 40], fill=c(mix(BG, GREEN, p)))
    ctext(d, (150, y), "✓", F(54), c(BG))
    ctext(d, (230 + (1 - p) * 60, y), label, F(54), c(mix(BG, WHITE, p)), "lm")

def sc_devops(d, t, al):
    c = lambda x: mix(BG, x, al)
    title(d, t, al, "DEVOPS", wt("Kaani DevOps", "DevOps"), GREEN, 290, 100)
    k = "Development and Operations"
    pd_, po = pop(t, wt(k, "Development")), pop(t, wt(k, "Operations"))
    pill(d, 220, 640, 300, 130, "DEV", GREEN, pd_, al, 52)
    pill(d, 860, 640, 300, 130, "OPS", GREEN, po, al, 52)
    pk = pop(t, wt(k, "kalisi"), .5)
    ctext(d, (540, 645), "∞", F(int(150 * (.6 + .4 * pk))), c(mix(BG, GREEN, pk)))
    ctext(d, (540, 780), "kalisi work", F(40), c(mix(BG, GREY, pk)))
    check_row(d, 940, "Problems share", pop(t, wt("Problems ni share", "Problems")), al)
    check_row(d, 1090, "Automation use", pop(t, wt("automation use", "automation")), al)
    check_row(d, 1240, "Better deployment", pop(t, wt("deployment process", "deployment")), al)

def sc_pipeline(d, t, al):
    c = lambda x: mix(BG, x, al)
    pill(d, 540, 330, 360, 80, "EXAMPLE", GREEN, pop(t, wt("Example ki")), al, 40)
    nodes = [("GITHUB PUSH", wt("developer code", "GitHub")), ("CI/CD PIPELINE", wt("CI/CD", "CI/CD")),
             ("BUILD", wt("CI/CD", "build")), ("TESTS", wt("tests run", "tests")), ("DEPLOY", wt("tests run", "deployment"))]
    ys = [490, 680, 870, 1060, 1250]
    for i, (lab, cue) in enumerate(nodes):
        p = pop(t, cue)
        act = ease(1 - (t - cue) / 1.0) if t >= cue else 0
        pill(d, 540, ys[i], 560, 110, lab, GREEN, p, al, 50, fill_p=act if p else 0)
        if i:
            pa = pop(t, cue - .3, .3)
            if pa:
                d.line([540, ys[i - 1] + 58, 540, ys[i] - 58], fill=c(mix(BG, GREEN, pa)), width=6)
    for lab, cue, cx in (("FASTER", wt("tests run", "faster"), 270), ("RELIABLE", wt("tests run", "reliable"), 810)):
        pill(d, cx, 1440, 440, 90, lab, WHITE, pop(t, cue), al, 44)

def sc_table(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (300, 320), "TRADITIONAL IT", F(44), c(mix(BG, GREY, pop(t, wt("Traditional IT lo manual"), .5))))
    ctext(d, (790, 320), "DEVOPS", F(54), c(mix(BG, GREEN, pop(t, wt("DevOps lo automation"), .5))))
    d.line([540, 270, 540, 1330], fill=c(DIM), width=4)
    rows = [("Manual work", "Automation", wt("Traditional IT lo manual", "manual"), wt("DevOps lo automation", "automation")),
            ("Separate teams", "Collaboration", wt("Traditional IT lo teams", "separate"), wt("DevOps lo collaboration", "collaboration")),
            ("Slow releases", "Frequent releases", wt("Traditional IT lo releases", "slow"), wt("DevOps practices", "frequent"))]
    for i, (l, r, cl, cr) in enumerate(rows):
        y = 560 + i * 280
        pl, pr = pop(t, cl), pop(t, cr)
        if pl: pill(d, 290, y, 440, 130, l, GREY, pl, al, 40)
        if pr: pill(d, 800, y, 440, 130, r, GREEN, pr, al, 40, fill_p=ease(1 - (t - cr) / .8) if t >= cr else 0)

def sc_remember(d, t, al):
    c = lambda x: mix(BG, x, al)
    k = "Remember! DevOps ante"
    ctext(d, (540, 300), "REMEMBER!", F(92), c(mix(BG, WHITE, pop(t, wt(k, "Remember!"), .4))))
    ctext(d, (540, 520), "DEVOPS", F(130), c(mix(BG, GREEN, pop(t, wt(k, "DevOps")))))
    pj = pop(t, wt(k, "just"), .4)
    ctext(d, (540, 700), "≠  JUST TOOLS", F(80), c(mix(BG, GREY, pj)))
    ps = pop(t, wt(k, "tools"), .4)
    if ps: d.line([440, 700, 880, 700], fill=c(mix(BG, RED, ps)), width=8)
    kc = "Collaboration, Automation,"
    for i, (lab, cue) in enumerate([("COLLABORATION", wt(kc, "Collaboration,")), ("AUTOMATION", wt(kc, "Automation,")),
                                    ("CONTINUOUS IMPROVEMENT", wt(kc, "Continuous"))]):
        pill(d, 540, 900 + i * 150, 860, 110, lab, GREEN, pop(t, cue), al, 46 if i < 2 else 40,
             fill_p=ease(1 - (t - cue) / .8) if t >= cue else 0)
    pi = pop(t, wt(kc, "important!"), .4)
    ctext(d, (540, 1390), "★ IMPORTANT ★", F(64), c(mix(BG, WHITE, pi)))

def sc_day4(d, t, al):
    c = lambda x: mix(BG, x, al)
    k = "Idi mana"
    ctext(d, (540, 760), "DAY 4  ✓", F(190), c(mix(BG, WHITE, pop(t, wt(k, "Day"), .5))))
    pb = pop(t, wt(k, "100"), .5)
    ctext(d, (540, 960), "100 DAYS OF DEVOPS", F(48), c(mix(BG, GREEN, pb)))
    rbox(d, [140, 1030, 940, 1070], c(mix(BG, DIM, pb)), None, 20)
    if pb: rbox(d, [140, 1030, 140 + 800 * .04 * ease((t - wt(k, "Day")) / 1.0) + 40, 1070], c(GREEN), None, 20)
    ctext(d, (540, 1130), "4 / 100", M(44), c(mix(BG, GREY, pb)))

def sc_day5(d, t, al):
    c = lambda x: mix(BG, x, al)
    k = "Day 5 lo"
    ctext(d, (540, 600), "DAY 5", F(210), c(mix(BG, WHITE, pop(t, wt(k, "Day"), .5))))
    ctext(d, (540, 850), "AGILE", F(130), c(mix(BG, GREEN, pop(t, wt(k, "Agile")))))
    ctext(d, (540, 990), "↔", F(90), c(mix(BG, GREY, pop(t, wt(k, "DevOps")))))
    ctext(d, (540, 1130), "DEVOPS", F(130), c(mix(BG, WHITE, pop(t, wt(k, "DevOps")))))
    q = pop(t, wt(k, "connection"), .4)
    ctext(d, (540, 1330), "CONNECTION?", F(76 + int(6 * math.sin(t * 6) * q)), c(mix(BG, GREEN, q)))

def sc_cta(d, t, al):
    c = lambda x: mix(BG, x, al)
    pl, pf = pop(t, wt("Useful", "Like"), .4), pop(t, wt("Follow"), .3)
    w = 330 * (1 + .06 * pl)
    if pl: rbox(d, [540 - w, 700, 540 + w, 850], c(BG), c(mix(BG, WHITE, pl)), 75, 5)
    ctext(d, (540, 775), "♥  LIKE", F(80), c(mix(BG, WHITE, pl)))
    w = 330 * (1 + .06 * pf + .02 * math.sin(t * 6))
    if pf: rbox(d, [540 - w, 950, 540 + w, 1100], mix(BG, GREEN, pf * al), None, 75)
    ctext(d, (540, 1025), "FOLLOW", M(76), (0, 0, 0) if pf > .5 else BG)

def main(audio, sync, out):
    PH[:] = json.load(open(sync))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                               capture_output=True, text=True).stdout)
    events = caption_events()
    sc = [(0, 3.4, sc_recap), (3.4, 9.3, sc_question), (9.3, 22.25, sc_traditional), (22.25, 30.0, sc_blame),
          (30.0, 41.2, sc_devops), (41.2, 53.25, sc_pipeline), (53.25, 71.1, sc_table), (71.1, 78.0, sc_remember),
          (78.0, 81.3, sc_day4), (81.3, 86.2, sc_day5), (86.2, dur + 1, sc_cta)]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
    for fi in range(int(math.ceil(dur * FPS))):
        t = fi / FPS
        im = background(); d = ImageDraw.Draw(im)
        for a, b, fn in sc:
            if a <= t < b: fn(d, t, min(ease((t - a) / .2), 1 - ease((t - (b - .2)) / .2)) if a > 0 else 1 - ease((t - (b - .2)) / .2))
        d.rectangle([0, 0, W * t / dur, 12], fill=GREEN)
        ctext(d, (W / 2, 70), "100 DAYS OF DEVOPS", M(30), GREY)
        caption(d, t, events)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
