"""Render the 'rich background + motion graphics' version of the edit."""
import os, sys, subprocess
from PIL import Image
from multiprocessing import Pool
from rlib import W, H, FPS, SS, Canvas
import rich, grade_final

HERE = os.path.dirname(os.path.abspath(__file__)); BASE = HERE + "/work/base.mp4"
TOTAL = grade_final.TOTAL

def render(args):
    i, raw = args; T = i / FPS
    frame = Image.frombytes("RGB", (W, H), raw)
    c = Canvas(rich.bg_image(T)); rich.overlays(c, frame, T, TOTAL)
    return c.result().tobytes()

def frames(start=0, count=None):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", BASE, "-vf", f"fps={FPS},tpad=stop_mode=clone:stop_duration={rich.END_HOLD}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3; i = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        if i >= start and (count is None or i < start + count): yield (i, b)
        i += 1

if __name__ == "__main__":
    out = sys.argv[1]
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]; want = {int(t * FPS): t for t in ts}; ims = []
        for i, b in frames():
            if i in want: ims.append(Image.frombytes("RGB", (W, H), render((i, b))).resize((360, 640)))
        sh = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): sh.paste(im, (k * 360, 0))
        sh.save(out); sys.exit()
    wavp = HERE + "/work/final_mix.wav"; grade_final.audio_mix(wavp)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wavp,
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fr in enumerate(pool.imap(render, frames(), chunksize=4)):
            ff.stdin.write(fr)
            if i % 150 == 0: print("frame", i, flush=True)
    ff.stdin.close(); ff.wait(); print("done", round(TOTAL, 2))
