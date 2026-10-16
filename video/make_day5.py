"""Day 5 (Agile and DevOps) video, 1080x1920, black / neon-green palette, synced to a voiceover.
Usage: python3 make_day5.py voiceover.mp3 day5-sync.json out.mp4
day5-sync.json comes from: python3 align_voiceover.py day5_phrases voiceover.mp3 day5-sync.json
Every animation and caption is keyed to a spoken word via T(phrase_index, word)."""
import json, math, subprocess, sys
from PIL import ImageDraw
import make_day4 as D4
from make_day3 import (F, M, W, H, FPS, BG, GREEN, WHITE, GREY, DIM, RED, ease, lerp, mix, pop,
                       ctext, rbox, background, caption)
from make_day4 import pill, check_row, title, clean

PH = D4.PH
def T(i, word=None, occ=0):
    """Start time of `word` (default: first word) of phrase number i."""
    p = PH[i]
    if word is None: return p["times"][0]
    n = 0
    for tk, tm in zip(p["text"].split(), p["times"]):
        if clean(tk).startswith(clean(word)):
            if n == occ: return tm
            n += 1
    raise KeyError((i, word))

def sc_recap(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 760), "DAY 4  ✓", F(190), c(mix(BG, WHITE, pop(t, T(0, "Day"), .5))))
    ctext(d, (540, 940), "Traditional IT vs DevOps", F(56), c(mix(BG, GREEN, pop(t, T(0, "Traditional")))))

def sc_question(d, t, al):
    c = lambda x: mix(BG, x, al)
    pill(d, 540, 430, 620, 90, "IMPORTANT QUESTION", GREEN, pop(t, T(1, "important"), .4), al, 38)
    ctext(d, (540, 660), "AGILE ?", F(150), c(mix(BG, WHITE, pop(t, T(2, "Agile")))))
    ctext(d, (540, 830), "↔", F(90), c(mix(BG, GREY, pop(t, T(3, "DevOps")))))
    ctext(d, (540, 1000), "DEVOPS ?", F(150), c(mix(BG, GREEN, pop(t, T(3, "DevOps")))))
    q = pop(t, T(3, "connection"), .4)
    ctext(d, (540, 1250), "CONNECTION?", F(84 + int(6 * math.sin(t * 6) * q)), c(mix(BG, WHITE, q)))

def sc_agile(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 290), "WHAT IS AGILE?", F(80), c(mix(BG, GREEN, pop(t, T(4, "Agile"), .5))))
    ps = pop(t, T(4, "software"), .5)
    split = ease((t - T(4, "small-small")) / .8)
    n, tot_w, gap = 5, 800, 16
    if ps:
        if split < .02:
            pill(d, 540, 560, 800, 130, "SOFTWARE DEVELOPMENT", WHITE, ps, al, 46)
        else:
            w = (tot_w - gap * (n - 1)) / n
            for i in range(n):
                x = 140 + i * (w + gap) + w / 2
                pill(d, x, 560, w * (.3 + .7 * split) , 130, f"{i + 1}", GREEN, split, al, 52, fill_p=ease(1 - (t - T(4, "small-small") - .15 * i) / .6) if t > T(4, "small-small") else 0)
            ctext(d, (540, 690), "small-small steps", F(44), c(mix(BG, GREY, split)))
    pd_ = pop(t, T(4, "divide"), .4)
    ctext(d, (540, 800), "DIVIDE", F(60), c(mix(BG, WHITE, pd_)))
    pf = pop(t, T(5, "feedback"), .5)
    if pf:
        pill(d, 540, 1000, 600, 110, "FEEDBACK", GREEN, pf, al, 54)
    pi = pop(t, T(5, "improve"), .5)
    if pi: d.line([540, 1055, 540, 1245], fill=c(mix(BG, GREEN, pi)), width=6)
    pill(d, 540, 1300, 600, 110, "IMPROVE", WHITE, pi, al, 54, fill_p=ease(1 - (t - T(5, "improve")) / .8) if t >= T(5, "improve") else 0)

def sc_example1(d, t, al):
    c = lambda x: mix(BG, x, al)
    pill(d, 540, 310, 360, 80, "EXAMPLE", GREEN, pop(t, T(6, "Example")), al, 40)
    pb = pop(t, T(7, "big"), .4)
    sp = ease((t - T(8, "small")) / .6)
    if sp < .05: pill(d, 540, 520, 800, 150, "BIG APPLICATION", WHITE, pb, al, 52)
    else:
        w = 185
        for i in range(4):
            pill(d, 140 + i * (w + 20) + w / 2, 520, w * (.3 + .7 * sp), 150, f"F{i + 1}", GREEN, sp, al, 54)
        ctext(d, (540, 650), "small features", F(44), c(mix(BG, GREY, sp)))
    steps = [("DEVELOP", T(9, "develop")), ("TEST", T(10, "test")), ("FEEDBACK", T(11, "feedback")), ("IMPROVE", T(11, "improvements"))]
    for i, (lab, cue) in enumerate(steps):
        y = 830 + i * 150
        pill(d, 540, y, 560, 110, lab, GREEN, pop(t, cue), al, 50, fill_p=ease(1 - (t - cue) / .8) if t >= cue else 0)
        if i:
            pa = pop(t, cue - .25, .25)
            if pa: d.line([540, y - 150 + 58, 540, y - 58], fill=c(mix(BG, GREEN, pa)), width=6)

def sc_fit(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 290), "WHERE DOES DEVOPS FIT?", F(60), c(mix(BG, GREEN, pop(t, T(12, "Ippudu"), .5))))
    pill(d, 540, 480, 640, 110, "AGILE", WHITE, pop(t, T(13, "Agile")), al, 56)
    pf = pop(t, T(13, "flexible"), .4)
    ctext(d, (540, 590), "fast + flexible", F(44), c(mix(BG, GREY, pf)))
    pa = pop(t, T(14, "DevOps") - .3, .3)
    if pa: d.line([540, 620, 540, 700], fill=c(mix(BG, GREEN, pa)), width=6)
    pill(d, 540, 780, 640, 110, "DEVOPS", GREEN, pop(t, T(14, "DevOps")), al, 56, fill_p=ease(1 - (t - T(14, "DevOps")) / .8))
    cells = [("BUILD", T(14, "build"), 300, 980), ("TEST", T(15), 780, 980), ("DEPLOY", T(16, "deploy"), 300, 1140), ("MONITOR", T(16, "monitor"), 780, 1140)]
    for lab, cue, x, y in cells:
        pill(d, x, y, 400, 110, lab, GREEN, pop(t, cue), al, 46, fill_p=ease(1 - (t - cue) / .8) if t >= cue else 0)

def sc_example2(d, t, al):
    c = lambda x: mix(BG, x, al)
    pill(d, 540, 310, 360, 80, "EXAMPLE", GREEN, pop(t, T(17, "Example")), al, 40)
    nodes = [("AGILE TEAM: NEW FEATURE", T(18, "Agile"), WHITE), ("CI/CD PIPELINE", T(19, "CI/CD"), GREEN),
             ("AUTOMATIC TEST ✓", T(20, "automatic"), GREEN), ("DEPLOY", T(20, "deploy"), GREEN)]
    for i, (lab, cue, col) in enumerate(nodes):
        y = 500 + i * 190
        pill(d, 540, y, 760, 120, lab, col, pop(t, cue), al, 44, fill_p=ease(1 - (t - cue) / .8) if t >= cue else 0)
        if i:
            pa = pop(t, cue - .25, .25)
            if pa: d.line([540, y - 190 + 63, 540, y - 63], fill=c(mix(BG, GREEN, pa)), width=6)
    ctext(d, (540, 1330), "DevOps tools", F(60), c(mix(BG, GREEN, pop(t, T(19, "tools"), .4))))

def sc_simple(d, t, al):
    c = lambda x: mix(BG, x, al)
    pill(d, 540, 340, 460, 90, "IN SHORT", GREEN, pop(t, T(21, "Simple"), .4), al, 40)
    pa = pop(t, T(22, "Agile"))
    rbox(d, [80, 520, 1000, 800], c(mix(BG, WHITE, .06 * pa)), c(mix(BG, WHITE, pa)), 40, 4) if pa else None
    ctext(d, (540, 590), "AGILE", F(80), c(mix(BG, WHITE, pa)))
    hr = pop(t, T(22, "right"), .4)
    ctext(d, (540, 710), "build the RIGHT software", F(46), c(mix(BG, mix(WHITE, GREEN, hr), pa)))
    pd_ = pop(t, T(23, "DevOps"))
    rbox(d, [80, 920, 1000, 1200], c(mix(BG, GREEN, .08 * pd_)), c(mix(BG, GREEN, pd_)), 40, 4) if pd_ else None
    ctext(d, (540, 990), "DEVOPS", F(80), c(mix(BG, GREEN, pd_)))
    hl = pop(t, T(23, "reliably"), .4)
    ctext(d, (540, 1110), "deliver + operate it RELIABLY", F(44), c(mix(BG, mix(WHITE, GREEN, hl), pd_)))

def sc_together(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 300), "AGILE + DEVOPS", F(90), c(mix(BG, GREEN, pop(t, T(24, "Rendu"), .5))))
    ctext(d, (540, 430), "kalisi work chesthe…", F(46), c(mix(BG, GREY, pop(t, T(24, "kalisi"), .4))))
    check_row(d, 640, "Faster releases", pop(t, T(24, "faster")), al)
    check_row(d, 800, "Quick feedback", pop(t, T(25, "feedback")), al)
    check_row(d, 960, "Continuous improvement", pop(t, T(25, "continuous")), al)

def sc_day5(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 760), "DAY 5  ✓", F(190), c(mix(BG, WHITE, pop(t, T(26, "Day"), .5))))
    pb = pop(t, T(26, "100"), .5)
    ctext(d, (540, 960), "100 DAYS OF DEVOPS", F(48), c(mix(BG, GREEN, pb)))
    rbox(d, [140, 1030, 940, 1070], c(mix(BG, DIM, pb)), None, 20)
    if pb: rbox(d, [140, 1030, 140 + 800 * .05 * ease((t - T(26, "Day")) / 1.0) + 40, 1070], c(GREEN), None, 20)
    ctext(d, (540, 1130), "5 / 100", M(44), c(mix(BG, GREY, pb)))

def sc_day6(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 600), "DAY 6", F(210), c(mix(BG, WHITE, pop(t, T(27, "Day"), .5))))
    ctext(d, (540, 850), "SDLC", F(190), c(mix(BG, GREEN, pop(t, T(27, "SDLC")))))
    ctext(d, (540, 1040), "Software Development", F(52), c(mix(BG, WHITE, pop(t, T(28, "software")))))
    ctext(d, (540, 1110), "Life Cycle", F(52), c(mix(BG, WHITE, pop(t, T(28, "development")))))
    q = pop(t, T(28, "work"), .4)
    ctext(d, (540, 1300), "ela work avuthundi?", F(60 + int(6 * math.sin(t * 6) * q)), c(mix(BG, GREEN, q)))

def sc_cta(d, t, al):
    c = lambda x: mix(BG, x, al)
    ctext(d, (540, 650), "DEVOPS JOURNEY", F(88), c(mix(BG, GREEN, pop(t, T(29, "DevOps"), .5))))
    ctext(d, (540, 790), "continues →", F(64), c(mix(BG, WHITE, pop(t, T(29, "continue"), .5))))
    pf = pop(t, T(29, "Follow"), .3)
    w = 330 * (1 + .06 * pf + .02 * math.sin(t * 6))
    if pf: rbox(d, [540 - w, 950, 540 + w, 1100], mix(BG, GREEN, pf * al), None, 75)
    ctext(d, (540, 1025), "FOLLOW", M(76), (0, 0, 0) if pf > .5 else BG)

def main(audio, sync, out):
    PH[:] = json.load(open(sync))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                               capture_output=True, text=True).stdout)
    events = D4.caption_events()
    sc = [(0, 4.6, sc_recap), (4.6, 10.9, sc_question), (10.9, 18.2, sc_agile), (18.2, 29.8, sc_example1),
          (29.8, 41.3, sc_fit), (41.3, 51.8, sc_example2), (51.8, 59.6, sc_simple), (59.6, 66.9, sc_together),
          (66.9, 70.2, sc_day5), (70.2, 75.9, sc_day6), (75.9, dur + 1, sc_cta)]
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
