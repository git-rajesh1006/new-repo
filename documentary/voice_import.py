"""Place a single supplied narration file onto the 5:00 timeline, sentence by sentence."""
import re, subprocess, numpy as np
import narration

def load(path, sr=24000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy(), sr

def sentences_audio(a, sr, min_gap=0.88, thr=0.012):
    """Split on pauses >= min_gap seconds. Returns [(start, end)] in seconds."""
    hop = int(0.01 * sr); n = len(a) // hop
    env = np.abs(a[:n * hop]).reshape(n, hop).max(1) > thr
    spans = []; i = 0
    while i < n:
        if env[i]:
            j = i; last = i
            while j < n and (j - last) * 0.01 < min_gap:
                if env[j]: last = j
                j += 1
            spans.append((i * 0.01, (last + 1) * 0.01)); i = last + 1
        else: i += 1
    return spans

def script_sentences():
    out = []
    for a, b, txt in narration.SEGMENTS:
        out.append([s for s in re.split(r"(?<=[.?!])\s+", txt)])
    return out

def pieces_from(path, pad=0.06):
    a, sr = load(path); spans = sentences_audio(a, sr); segs = script_sentences()
    flat = [s for seg in segs for s in seg]
    assert len(spans) == len(flat), f"found {len(spans)} spoken sentences, script has {len(flat)}"
    pieces = []; k = 0; log = []
    for (a0, b0, _), sents in zip(narration.SEGMENTS, segs):
        clips = []
        for s in sents:
            st, en = spans[k]; k += 1
            clips.append((s, a[max(0, int((st - pad) * sr)):int((en + pad) * sr)]))
        # window for this segment + any explicit anchor times (key visual beats)
        if a0 == 0: anchors = [1.3, 4.75]
        elif a0 == 285: anchors = [285.7, 289.4]
        else: anchors = [a0 + 0.5]
        end_lim = {0: 14.6, 285: 297.8, 298: 299.9}.get(a0, b0 - 0.3)
        start = 296.4 if a0 == 298 else anchors[0]
        if a0 in (0, 285):   # one piece per sentence at its anchor
            for (s, c), st in zip(clips, anchors):
                pieces.append(dict(start=st, dur=len(c) / sr, text=s, au=c, sr=sr, sents=[(s, 0.0, len(c) / sr)])); log.append((st, len(c) / sr, s[:50]))
            continue
        speech = sum(len(c) for _, c in clips) / sr; n_gap = len(clips) - 1; room = end_lim - start
        gap_s = float(np.clip((room * 0.93 - speech) / max(1, n_gap), 0.25, 1.6)) if n_gap else 0.0
        if speech + gap_s * n_gap > room:
            f = min(1.35, (speech + 0.25 * n_gap) / room)
            clips = [(s, atempo(c, sr, f)) for s, c in clips] if f > 1 else clips; gap_s = 0.25
        parts = []; off = 0.0; sents_t = []
        for i, (s, c) in enumerate(clips):
            sents_t.append((s, off, len(c) / sr)); parts.append(c); off += len(c) / sr
            if i < n_gap: parts.append(np.zeros(int(gap_s * sr), np.float32)); off += gap_s
        audio = np.concatenate(parts); dur = len(audio) / sr
        pieces.append(dict(start=start, dur=dur, text=" ".join(sents), au=audio, sr=sr, sents=sents_t))
        log.append((start, dur, " ".join(sents)[:50]))
    return pieces, log

def atempo(x, sr, f):
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", "-af", f"atempo={f}", "-f", "f32le", "-"],
                       input=x.tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()
