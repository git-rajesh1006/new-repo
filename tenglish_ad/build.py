"""Build the Tenglish vertical ad: captions (timed to the narration), music/SFX, optional ElevenLabs voice-over.
  python3 build.py out.mp4                         # draft: captions timed to the planned windows, no voice
  python3 build.py out.mp4 --voice clips_dir/      # 01.mp3..12.mp3 (one file per clip), fitted to the windows
  python3 build.py out.mp4 --voice one_file.mp3    # single file; clips split on pauses (must find exactly 12)
"""
import sys, os, re, math, wave, glob, subprocess, random
import numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool
import rlib
from rlib import W, H, FPS, SS, clamp, font, TERRA, INK
import scenes, script_te

SR = 44100; TOTAL = script_te.TOTAL
WORDS = []        # (start, end, word, clip_index)
CLIPSPAN = []     # (start, end) actual speech span per clip

def syl(w):
    w = re.sub(r"[^a-zA-Z]", "", w.lower()); return max(1, len(re.findall(r"[aeiouy]+", w)))

def plan(spans):
    """spans: [(start, dur)] per clip -> word timings proportional to syllables."""
    WORDS.clear(); CLIPSPAN.clear()
    for i, ((a, b, text), (st, dur)) in enumerate(zip(script_te.CLIPS, spans)):
        words = text.split(); wt = [syl(w) + (0.6 if re.search(r"[.,?!…]$", w) else 0) for w in words]; tot = sum(wt); t0 = st
        CLIPSPAN.append((st, st + dur))
        for w, x in zip(words, wt):
            d = dur * x / tot; WORDS.append((t0, t0 + d, w, i)); t0 += d

def groups():
    """Caption groups of <=3 words (never crossing a clip)."""
    out = []; cur = []
    for k, (s, e, w, ci) in enumerate(WORDS):
        if cur and (cur[0][3] != ci or len(cur) >= 3): out.append(cur); cur = []
        cur.append((s, e, w, ci))
        if re.search(r"[.?!…]$", w) or (w.endswith(",") and len(cur) >= 2): out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def caption_img(T, grp, dark, orange):
    s0, e0 = grp[0][0], grp[-1][1]; size = 46
    lay = Image.new("RGBA", (W * SS, 130 * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = font("sans", size); sp = f.getlength(" ") * 1.55
    ws = [f.getlength(w[2]) for w in grp]; tot = sum(ws) + sp * (len(grp) - 1)
    x = (W * SS - tot) / 2; cy = 65 * SS
    for (s, e, w, ci), wd in zip(grp, ws):
        cur = s <= T < e; past = T >= e
        if cur:
            pad = 14 * SS; d.rounded_rectangle([x - pad, cy - 36 * SS, x + wd + pad, cy + 36 * SS], radius=14 * SS, fill=((26, 26, 30) if orange else TERRA) + (255,))
            col = (255, 255, 255)
        else:
            col = ((255, 255, 255) if past else (150, 140, 146)) if dark else (((255, 255, 255) if past else (255, 220, 208)) if orange else (INK if past else (178, 174, 170)))
        d.text((x, cy), w, font=f, fill=col + (255,), anchor="lm"); x += wd + sp
    return lay.resize((W, 130), Image.LANCZOS)

def scene_at(T):
    for a, b, fn in scenes.SCENES:
        if a <= T < b: return a, b, fn
    return scenes.SCENES[-1]

GROUPS = []
def render(frame):
    T = frame / FPS
    a, b, fn = scene_at(T)
    c = fn(T - a, T); img = c.result()
    if T - a < .18 and a > 0:   # quick cross-fade on scene change
        pa, pb, pf = scene_at(a - .001); img = Image.blend(pf(T - pa, T).result(), img, rlib.ease((T - a) / .18))
    dark = 18.45 < T < 27.0; orange = 6.3 <= T < 8.6
    for g in GROUPS:
        if g[0][0] - .12 <= T < g[-1][1] + .22:
            lay = caption_img(T, g, dark, orange); img = img.convert("RGBA"); img.alpha_composite(lay, (0, 1040)); img = img.convert("RGB"); break
    arr = np.asarray(img, dtype=np.float32); arr += np.random.default_rng(frame).normal(0, 1.3, arr.shape[:2])[..., None]
    return np.clip(arr, 0, 255).astype(np.uint8).tobytes()

# ------------------------------------------------------------------ audio
def music_sfx():
    n = int(TOTAL * SR); out = np.zeros(n, np.float32); rng = np.random.default_rng(4)
    def tt(d): return np.arange(int(d * SR)) / SR
    def add(st, sig, g=1.0):
        i = int(st * SR)
        if 0 <= i < n: j = min(n, i + len(sig)); out[i:j] += (sig[:j - i] * g).astype(np.float32)
    kick = lambda: (lambda x: np.sin(2 * np.pi * (50 + 90 * np.exp(-x * 30)) * x) * np.exp(-x * 10))(tt(.25))
    hat = lambda: (lambda x: rng.normal(0, 1, len(x)) * np.exp(-x * 100))(tt(.04))
    pluck = lambda f, d=.4: (lambda x: (np.sin(2 * np.pi * f * x) + .4 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 8))(tt(d))
    pad = lambda f, d, g=.07: (lambda x: (np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 1.005 * x)) * np.minimum(1, x / .6) * np.clip((d - x) / .6, 0, 1) * g)(tt(d))
    tick = lambda f=2400, d=.03: (lambda x: np.sin(2 * np.pi * f * x) * np.exp(-x * 140))(tt(d))
    def whoosh(d=.45):
        x = rng.normal(0, 1, int(d * SR)); y = np.zeros_like(x); a = 0.0
        for i in range(len(x)): a += (.04 + .45 * i / len(x)) * (x[i] - a); y[i] = a
        return y * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.4 * 2.5
    bpm = 120; beat = 60 / bpm
    chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
    t0 = 0.0; bar = 0
    while t0 < TOTAL:
        ch = chords[bar % 4]; g = .05 + .05 * clamp(t0 / 6)
        add(t0, pad(ch[0] / 2, 4 * beat + .3, .09), 1)
        for k in range(8): add(t0 + k * beat / 2, pluck(ch[k % 3] * (2 if k % 4 == 3 else 1)), g)
        if t0 >= 3.9:
            for k in range(4): add(t0 + k * beat, kick(), .28); add(t0 + k * beat + beat / 2, hat(), .04)
        t0 += 4 * beat; bar += 1
    for a, b, fn in scenes.SCENES[1:]: add(a - .1, whoosh(), .22)
    for i in range(6): add(1.0 + i * .28 + .25, tick(), .35)          # toggles
    add(6.3, kick(), .9); add(7.9, kick(), .6); add(18.0, kick(), .9)
    for i in range(5): add(9.8 + i * .13 + .1, tick(1800 + 100 * i), .3)
    for tm in (20.0,): pass
    for i, tm in enumerate((28.9, 29.35)): add(tm, tick(2200, .05), .35)
    add(31.3, pluck(880, .6), .3); add(31.3, pluck(1320, .6), .2)
    add(32.1, tick(1500, .05), .4); add(32.4, tick(1700, .05), .4)
    for i in range(7): add(33.1 + i * .08, tick(1900 + 60 * i, .02), .2)
    out *= np.clip((TOTAL - np.arange(n) / SR) / .8, 0, 1)
    return out

def load_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).copy(); return a

def trim_silence(a, thr=.012):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(0, idx[0] - int(.03 * SR)):idx[-1] + int(.06 * SR)] if len(idx) else a

def atempo(a, f):
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={f:.4f}", "-f", "f32le", "-"], input=a.tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()

def split_single(a, n_expected, gap=.85):
    hop = int(.01 * SR); k = len(a) // hop; env = np.abs(a[:k * hop]).reshape(k, hop).max(1) > .012
    spans = []; i = 0
    while i < k:
        if env[i]:
            last = i; j = i
            while j < k and (j - last) * .01 < gap:
                if env[j]: last = j
                j += 1
            spans.append((i * hop, (last + 1) * hop)); i = last + 1
        else: i += 1
    if len(spans) != n_expected: raise SystemExit(f"found {len(spans)} spoken clips in the file, expected {n_expected}; please send 12 separate files (01.mp3 .. 12.mp3)")
    return [a[s:e] for s, e in spans]

def fit_voice(src):
    n = len(script_te.CLIPS)
    if os.path.isdir(src):
        files = sorted(glob.glob(os.path.join(src, "*.mp3")) + glob.glob(os.path.join(src, "*.wav")) + glob.glob(os.path.join(src, "*.m4a")))
        if len(files) != n: raise SystemExit(f"{src} has {len(files)} audio files, expected {n}")
        clips = [trim_silence(load_audio(f)) for f in files]
    else: clips = [trim_silence(c) for c in split_single(load_audio(src), n)]
    voice = np.zeros(int(TOTAL * SR), np.float32); spans = []; report = []
    for (a, b, text), c in zip(script_te.CLIPS, clips):
        win = b - a - .12; d = len(c) / SR
        if d > win: f = min(1.4, d / win); c = atempo(c, f); report.append(f"x{f:.2f}")
        else: report.append("ok")
        st = a + .06; i = int(st * SR); voice[i:i + len(c)] += c[:len(voice) - i]; spans.append((st, len(c) / SR))
    voice /= max(1e-6, np.abs(voice).max()) / .95
    print("clip fit:", " ".join(report)); return voice, spans

def write_wav(path, mono):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mono, mono], 1) * 32767).astype("<i2").tobytes())

if __name__ == "__main__":
    out = sys.argv[1]; voice = None
    if "--voice" in sys.argv: voice, spans = fit_voice(sys.argv[sys.argv.index("--voice") + 1])
    else: spans = [(a + .05, (b - a) * .9) for a, b, _ in script_te.CLIPS]
    plan(spans); GROUPS.extend(groups())
    m = music_sfx()
    if voice is not None:
        k = int(.2 * SR); env = np.convolve((np.abs(voice) > .03).astype(np.float32), np.ones(k, np.float32) / k, "same"); duck = 1 - .6 * np.clip(env * 3, 0, 1)
        mix = np.tanh(m * duck * 1.0 + voice * 1.1)
    else: mix = np.tanh(m * 1.1)
    mix = mix / np.abs(mix).max() * .9; wavp = out + ".wav"; write_wav(wavp, mix)
    if "--preview" in sys.argv:
        for tt in [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]:
            Image.frombytes("RGB", (W, H), render(int(tt * FPS))).resize((360, 640)).save(f"{out}_{tt:05.1f}.png")
        sys.exit()
    nfr = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wavp, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(TOTAL), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fr in enumerate(pool.imap(render, range(nfr), chunksize=6)):
            ff.stdin.write(fr)
            if i % 150 == 0: print("frame", i, flush=True)
    ff.stdin.close(); ff.wait()
