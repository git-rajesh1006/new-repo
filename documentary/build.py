"""Build the 5:00 documentary: narration (offline TTS) -> music/SFX -> frames -> MP4 (+ SRT)."""
import sys, math, wave, subprocess, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool
import lib, scenes, narration
from lib import W, H, FPS, SS, clamp, ease

TOTAL = 300.0; SR = 44100
OVR = {0: [(1.30, 4.55, "My team took two to three days to make a YouTube intro."), (4.75, 14.6, "What if an AI could make its version in just forty minutes?")],
       285: [(285.7, 289.0, "AI can accelerate the workflow."), (289.4, 297.8, "But direction, judgment, and the final creative decisions still matter.")]}

def build_voice():
    pieces = []
    for a, b, txt in narration.SEGMENTS:
        if a in OVR: plan = OVR[a]
        elif a == 298: plan = [(296.6, 299.85, txt)]
        else: plan = [(a + 0.55 if a else 0.7, b - 0.4, txt)]
        for st, en, tx in plan:
            rate, au = narration.fit(tx, 0.95 * (en - st))
            pieces.append(dict(start=st, dur=len(au) / narration.SR, text=tx, rate=rate, au=au))
    return pieces

def voice_track(pieces):
    n = int(TOTAL * SR); v = np.zeros(n, np.float32)
    for p in pieces:
        a = np.interp(np.arange(int(p["dur"] * SR)) / SR, np.arange(len(p["au"])) / narration.SR, p["au"]).astype(np.float32)
        i = int(p["start"] * SR); j = min(n, i + len(a)); v[i:j] += a[:j - i]
    return v / max(1e-6, np.abs(v).max()) * 0.95

# ---------------------------------------------------------------- music & sfx
def music_and_sfx(voice_env_dummy=None):
    n = int(TOTAL * SR); out = np.zeros(n, np.float32); rng = np.random.default_rng(11)
    def tt(d): return np.arange(int(d * SR)) / SR
    def add(st, sig, g=1.0):
        i = int(st * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(sig)); out[i:j] += (sig[:j - i] * g).astype(np.float32)
    def kick(f=52, d=.28):
        x = tt(d); return np.sin(2 * np.pi * (f + 90 * np.exp(-x * 32)) * x) * np.exp(-x * 11)
    def hat(d=.04): x = tt(d); return rng.normal(0, 1, len(x)) * np.exp(-x * 90)
    def clap(d=.12): x = tt(d); return rng.normal(0, 1, len(x)) * np.exp(-x * 30) * (1 + .6 * np.sin(x * 900))
    def pluck(f, d=.5):
        x = tt(d); return (np.sin(2 * np.pi * f * x) + .45 * np.sin(4 * np.pi * f * x) + .2 * np.sin(6 * np.pi * f * x)) * np.exp(-x * 7)
    def bass(f, d=.45):
        x = tt(d); return (np.sin(2 * np.pi * f * x) + .35 * np.sin(4 * np.pi * f * x)) * np.minimum(1, x * 80) * np.exp(-x * 3.2)
    def pad(f, d, g=.1):
        x = tt(d); e = np.minimum(1, x / 1.0) * np.clip((d - x) / 1.0, 0, 1)
        return (np.sin(2 * np.pi * f * x) + .6 * np.sin(2 * np.pi * f * 1.004 * x) + .3 * np.sin(2 * np.pi * f * .5 * x)) * e * g
    def tick(f=2800, d=.02): x = tt(d); return np.sin(2 * np.pi * f * x) * np.exp(-x * 160)
    def whoosh(d=.55, up=True):
        x = rng.normal(0, 1, int(d * SR)); y = np.zeros_like(x); a = 0.0; k = len(x)
        for i in range(k):
            al = 0.03 + 0.5 * ((i / k) if up else (1 - i / k)); a += al * (x[i] - a); y[i] = a
        e = np.sin(np.pi * np.linspace(0, 1, k)) ** 1.5; return y * e * 3.0
    def impact(d=1.6, f=42):
        x = tt(d); return (np.sin(2 * np.pi * (f + 120 * np.exp(-x * 18)) * x) * np.exp(-x * 2.4) + rng.normal(0, 1, len(x)) * np.exp(-x * 14) * .5)
    def chime(f=880, d=.9): x = tt(d); return (np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 1.5 * x)) * np.exp(-x * 4)
    def reverb(sig, d=2.4):
        ir = rng.normal(0, 1, int(d * SR)) * np.exp(-tt(d) * 2.6); ir[0] = 1
        return np.convolve(sig, ir[:int(d * SR)], "full")[:len(sig)] * .02
    A = {"Am": (110, 130.8, 164.8), "F": (87.3, 110, 130.8), "C": (65.4 * 2, 82.4 * 2, 98 * 2), "G": (98, 123.5, 146.8), "Cmaj": (130.8, 164.8, 196)}
    prog_min = ["Am", "F", "C", "G"]; bars = {"Am": 55, "F": 43.65, "C": 65.4, "G": 49}
    beat = 0.5
    # --- drone + riser (0-40)
    t = np.arange(n) / SR
    out += (0.035 * np.sin(2 * np.pi * 55 * t) + 0.02 * np.sin(2 * np.pi * 82.4 * t)) * np.clip(t / 10, 0, 1) * np.clip((40 - t) / 2, 0, 1) * (0.7 + .3 * np.sin(t * .8))
    for i, st in enumerate((0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0)): pass
    ph_ = 0.0
    seg_ = t[int(7 * SR):int(15 * SR)]; f_ = 110 * 2 ** ((seg_ - 7) / 8 * 1.5)
    out[int(7 * SR):int(15 * SR)] += 0.05 * np.sin(2 * np.pi * np.cumsum(f_) / SR) * np.linspace(0, 1, len(seg_))
    # ticking 0-40
    s = 0.2
    while s < 4.2: add(s, tick(2400, .03), .5); s += 1.0
    s = 4.2
    while s < 40: add(s, tick(3300, .015), .12 if s < 15 else .07); s += 0.5
    # --- pulse 15/40 .. 170
    def drums(a, b, kg=.4, hatg=.05, clapg=0.0, off=0):
        s = a
        while s < b:
            add(s, kick(), kg)
            add(s + beat / 2, hat(), hatg); add(s, hat(.02), hatg * .5)
            k_ = int(round((s - a) / beat))
            if clapg and k_ % 2 == 1: add(s, clap(), clapg)
            s += beat
    def harmony(a, b, arp_g=.06, pad_g=.07, bass_g=.2, eighths=False, scale=1.0, prog=prog_min):
        s = a; bar = 0
        while s < b:
            ch = prog[bar % len(prog)]; notes = A[ch]
            add(s, pad(notes[0], 4 * beat * 1.1, pad_g), 1)
            add(s, bass(bars.get(ch, notes[0] / 2) * scale, .9), bass_g)
            if eighths:
                for k in range(4): add(s + k * beat, bass(bars.get(ch, notes[0] / 2) * scale * (2 if k % 2 else 1), .3), bass_g * .7)
            for k in range(8): add(s + k * beat / 2, pluck(notes[k % 3] * (2 if k % 4 == 3 else 1) * (2 if scale > 1 else 1), .4), arp_g * (0.6 + 0.4 * (k % 2 == 0)))
            s += 4 * beat; bar += 1
    drums(40, 170, .22, .035); harmony(40, 170, .045, .06, .16)
    drums(15, 40, .0, .0)  # (placeholder, silent)
    for s in np.arange(28, 40, 0.5): add(s, kick(), .15)
    # --- groove 170-240
    drums(170, 240, .42, .06, .12); harmony(170, 240, .08, .06, .22, eighths=True)
    for s in np.arange(170, 240, beat / 2): add(s + beat / 4, hat(.025), .03)
    # --- restrained motif 240-265
    s = 240.0
    while s < 265:
        add(s, pluck(329.6, .9), .12); add(s + 1.0, pluck(440, 1.1), .12)
        if int((s - 240) / 4) % 2 == 0: add(s, pad(110, 4.2, .05), 1)
        s += 2.0
    # --- optimistic 265-298
    optim = ["C", "G", "Am", "F"]; A["C"] = (130.8, 164.8, 196); A["G"] = (98 * 2, 123.5 * 2, 146.8 * 2)
    harmony(265, 298, .07, .09, .15, scale=1.0, prog=optim)
    for s in np.arange(280, 298, beat): add(s, kick(), .18); add(s + beat / 2, hat(), .03)
    for i, s in enumerate(np.arange(285, 298, 4 * beat)): add(s, pad(261.6 * (1 + (i % 2) * .5), 4.5, .05), 1)
    # --- final impact + reverb tail
    add(298.0, impact(2.0, 40), 1.1)
    tail = np.zeros(n, np.float32); tail[int(298 * SR):int(298.4 * SR)] = out[int(298 * SR):int(298.4 * SR)]
    out += reverb(tail) * 4
    # fade music into scene 16 emphasis
    # ------ sfx
    for st, en, fn, tr in scenes.SCENES[1:]: add(st - 0.25, whoosh(.55), .22)
    add(1.5, impact(1.8, 38), 1.0); add(4.2, hat(.25), .5); add(4.6, impact(1.4, 48), .9)
    add(9.5, whoosh(1.6), .25)
    add(15 + .5, chime(660, .5), .1); add(15 + 6.0, impact(1.0, 55), .5)
    for i in range(10): add(28 + 5.2 + i * .35 + .5, tick(1800, .05), .28)
    add(28 + 3.2, hat(.3), .4)
    add(42 + .7, impact(1.0, 50), .55)
    for i in range(9): add(58 + .8 + i * 1.5 + .45, tick(2200, .05), .35); add(58 + .8 + i * 1.5 + .45, chime(1320, .25), .06)
    for i in range(12): add(75 + 5.6 + i * .25 + .4, tick(1500, .04), .25)
    add(75 + 20.0, whoosh(3.6, True), .25); add(75 + 23.6, chime(880, 1.2), .25); add(75 + 23.6, chime(1320, 1.2), .15)
    for i in range(12): add(100 + 6.5 + (i % 4) * .3 + .1 + i * .08, tick(1200, .05), .18)
    add(100 + 13.0, whoosh(.8, False), .2); add(100 + 18.9, impact(.8, 60), .45); add(100 + 21.5, tick(600, .12), .5)
    s = 125 + 0.8
    for i, (line, g) in enumerate(scenes.CODE):
        for k in range(0, len(line), 2): add(125 + 0.8 + i * 1.8 + k / 34, tick(1900 + (k % 5) * 90, .015), .22)
    add(125 + 11.4, chime(1760, 1.0), .14); add(125 + 16.5 + 4.0, chime(990, 1.0), .2)
    add(148 + 14.5, whoosh(.7), .25)
    for i in range(4): add(148 + 5.0 + i * 3.0 + .4, tick(2000, .05), .3)
    for tt_ in (1.5, 3.0): add(170 + tt_, impact(.7, 70), .4)
    for i in range(3): add(170 + 10.5 + i * 1.6, whoosh(.4), .25); add(170 + 10.5 + i * 1.6 + .3, tick(1000, .06), .35)
    add(170 + 18.5, impact(.9, 60), .5); add(170 + 19.2, chime(1500, .8), .2)
    for i in range(5): add(200 + .3 + i * .35 + .5, tick(1600 + 200 * i, .05), .3)
    for x in (4.5, 9.0, 13.5): add(200 + x, whoosh(.5), .2)
    for x in (2.5, 10.5, 15.0): add(200 + x, impact(.7, 50), .35)
    for j in range(4): add(220 + 3 + j * 1.6 + .3, chime(1000 + 100 * j, .4), .12)
    for i in range(5): add(240 + .6 + i * .7 + .4, tick(2400, .03), .2)
    for i in range(12): add(265 + 4.0 + i * .5, tick(1300, .04), .12)
    add(265 + 4.0, whoosh(2.0), .15)
    for x in (9.0, 11.5, 14.0): add(265 + x, chime(1100, .6), .12)
    add(285 + 5, whoosh(1.6), .12)
    add(298 + .95, impact(1.2, 70), .6)
    return out

def mix_audio(pieces):
    v = voice_track(pieces); m = music_and_sfx()
    n = len(v); k = int(0.22 * SR)
    env = np.convolve((np.abs(v) > 0.03).astype(np.float32), np.ones(k, np.float32) / k, "same")
    duck = 1 - 0.62 * np.clip(env * 3, 0, 1)
    mix = np.tanh(m * duck * 1.0 + v * 1.15)
    mix *= np.clip(np.arange(n) / (0.05 * SR), 0, 1)
    peak = np.abs(mix).max(); mix = mix / peak * 0.89
    return mix, v, m

def write_wav(path, mix):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix, mix], 1) * 32767).astype("<i2").tobytes())

# ---------------------------------------------------------------- captions
CYANW = {"claude", "opus", "5.5", "chatgpt", "6", "astra", "ai", "saas", "youtube"}
YELW = {"two", "three", "forty", "days", "minutes", "40", "2–3", "render", "time"}
CAPS = []   # (start, end, text)

def build_captions(pieces):
    for p in pieces:
        words = p["text"].split(); chunks = []; cur = []
        for w_ in words:
            cur.append(w_)
            if len(cur) >= 7 or (w_[-1] in ".?!:" and len(cur) >= 3) or (w_[-1] == "," and len(cur) >= 5): chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        total = sum(len(" ".join(c_)) for c_ in chunks); t0 = p["start"]
        for c_ in chunks:
            d = p["dur"] * len(" ".join(c_)) / total; CAPS.append((t0, t0 + d, " ".join(c_))); t0 += d

def srt_time(x): ms = int(round(x * 1000)); return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
def write_srt(path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, tx) in enumerate(CAPS, 1): f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{tx}\n\n")

def caption_layer(text):
    h = 120; lay = Image.new("RGBA", (W * SS, h * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = lib.font(46); words = text.split(); sp = f.getlength(" ")
    tw = sum(f.getlength(w_) for w_ in words) + sp * (len(words) - 1)
    x0 = (W * SS - tw) / 2; pad = 30 * SS
    d.rounded_rectangle([x0 - pad, 14 * SS, x0 + tw + pad, 94 * SS], radius=26 * SS, fill=(2, 5, 14, 190))
    x = x0
    for w_ in words:
        k = w_.strip(".,?!:;—’'").lower()
        col = lib.YELLOW if k in YELW else (lib.CYAN if k in CYANW else (255, 255, 255))
        d.text((x, 54 * SS), w_, font=f, fill=col, anchor="lm"); x += f.getlength(w_) + sp
    return lay.resize((W, h), Image.LANCZOS)

# ---------------------------------------------------------------- frames
def scene_img(i, T):
    st, en, fn, tr = scenes.SCENES[i]
    c = lib.Canvas(T=T); fn(c, T - st, T)
    return c.img.resize((W, H), Image.LANCZOS)

def render(frame):
    T = frame / FPS
    i = max(k for k, s in enumerate(scenes.SCENES) if s[0] <= T + 1e-9) if T < TOTAL else len(scenes.SCENES) - 1
    st, en, fn, tr = scenes.SCENES[i]
    img = scene_img(i, T); lt = T - st; D = 0.5
    if i > 0 and tr != "cut" and lt < D:
        p = ease(lt / D); prev = scene_img(i - 1, T)
        if tr == "wipe":
            x = int(W * p); m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([0, 0, x, H], fill=255)
            img = Image.composite(img, prev, m); d = ImageDraw.Draw(img); d.rectangle([x - 4, 0, x + 4, H], fill=lib.CYAN)
        elif tr == "whip":
            canvas = Image.new("RGB", (W, H), lib.DARK); off = int(W * p)
            canvas.paste(prev, (-off, 0)); canvas.paste(img, (W - off, 0))
            canvas = canvas.filter(ImageFilter.GaussianBlur(radius=40 * math.sin(math.pi * p) ** 2 + 0.01)) if False else canvas
            blur = Image.blend(canvas.transform(canvas.size, Image.AFFINE, (1, 0, -30 * math.sin(math.pi * p), 0, 1, 0)), canvas, 0.5)
            img = blur
        else:
            img = Image.blend(prev, img, p)
    # captions
    for a, b, tx in CAPS:
        if a <= T < b + 0.0:
            lay = caption_layer(tx); img = img.convert("RGBA"); img.alpha_composite(lay, (0, H - 120)); img = img.convert("RGB"); break
    arr = np.asarray(img, dtype=np.float32)
    arr *= VIG; arr += np.random.default_rng(frame).normal(0, 1.6, arr.shape[:2])[..., None]
    return np.clip(arr, 0, 255).astype(np.uint8).tobytes()

yy, xx = np.mgrid[0:H, 0:W]
VIG = np.clip(1.06 - 0.34 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), 0.55, 1)[..., None].astype(np.float32)

if __name__ == "__main__":
    out = sys.argv[1]
    pieces = build_voice(); build_captions(pieces)
    for p in pieces: print("%6.1f +%5.2fs rate=%3d  %s" % (p["start"], p["dur"], p["rate"], p["text"][:60]))
    mix, v, m = mix_audio(pieces); wavp = out + ".wav"; write_wav(wavp, mix); write_srt(out.replace(".mp4", ".srt"))
    print("audio peak", np.abs(mix).max())
    if "--audio-only" in sys.argv: sys.exit()
    if "--preview" in sys.argv:
        for tt in [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]:
            Image.frombytes("RGB", (W, H), render(int(tt * FPS))).resize((960, 540)).save(f"{out}_{tt:06.1f}.png")
        sys.exit()
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wavp,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", "300",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fr in enumerate(pool.imap(render, range(n), chunksize=6)):
            ff.stdin.write(fr)
            if i % 300 == 0: print("frame", i, flush=True)
    ff.stdin.close(); ff.wait()
