"""Align a known script to a voiceover WITHOUT an ASR model.
1) find acoustic phrases (speech segments split on short pauses) and count syllable nuclei in each;
2) DP: partition the script's words into consecutive groups, one per phrase, so each group's syllable
   count matches the phrase's nuclei count (pauses at commas/sentence ends are preferred cut points);
3) inside a phrase, words are placed by syllable position.
Usage: python align.py <audio> <script.txt> -o words.json   (script: one sentence per line)"""
import argparse, json, re, subprocess
import numpy as np
from scipy.signal import butter, sosfiltfilt, find_peaks

def load(path, sr=16000):
    raw = subprocess.run(["ffmpeg","-v","error","-i",path,"-ac","1","-ar",str(sr),"-f","f32le","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw, np.float32), sr

SPECIAL = {"devops":2,"ci/cd":4,"github":2,"100":2,"1":1,"2":1,"dev":1,"ops":1,"sdlc":4}
def syl(word):
    w = re.sub(r"[^\w/]", "", word.lower())
    if w in SPECIAL: return SPECIAL[w]
    w2 = re.sub(r"(aa|ee|oo|ai|au|ei|ie|ou|ea|io)", "V", w)
    n = len(re.findall(r"[aeiouyV]+", w2))
    if w.endswith("e") and not w.endswith(("ee","te","de","ge")) and n > 1: n -= 1
    return max(1, n)

def phrases(x, sr):
    hop = int(.01*sr); n = len(x)//hop
    db = 20*np.log10(np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)+1e-12) for i in range(n)]))
    thr = max(np.percentile(db, 10) + 8, -50); sp = db > thr
    segs, i = [], 0
    while i < n:
        if sp[i]:
            j = i
            while j < n and (sp[j] or sp[j+1:j+9].any()): j += 1
            segs.append((i*.01, j*.01)); i = j
        else: i += 1
    segs = [s for s in segs if s[1]-s[0] > .10]
    # syllable nuclei: smoothed envelope of the speech band
    sos = butter(4, [300, 3000], "bandpass", fs=sr, output="sos"); y = sosfiltfilt(sos, x)
    env = np.sqrt(np.convolve(y**2, np.ones(int(.04*sr))/int(.04*sr), "same"))
    e10 = env[::hop][:n]; e10 = e10 / (e10.max() + 1e-9)
    pk, _ = find_peaks(e10, distance=7, prominence=.035)
    out = []
    for a, b in segs:
        c = int(((pk*.01 >= a) & (pk*.01 <= b)).sum())
        out.append({"start": a, "end": b, "nuc": max(1, c), "peaks": [round(float(p*.01),3) for p in pk if a <= p*.01 <= b]})
    return out

def align(segs, sentences):
    words = []                                     # (token, sentence_end?, comma_after?)
    for si, s in enumerate(sentences):
        toks = s.split()
        for ti, t in enumerate(toks):
            words.append({"w": t, "syl": syl(t), "send": ti == len(toks)-1, "comma": t.endswith((",", ":")) , "sent": si})
    W, S = len(words), len(segs)
    cum = np.concatenate([[0], np.cumsum([w["syl"] for w in words])])
    INF = 1e18
    dp = np.full((S+1, W+1), INF); bk = np.zeros((S+1, W+1), int); dp[0][0] = 0
    for s in range(1, S+1):
        seg = segs[s-1]; gap = seg["start"] - segs[s-2]["end"] if s > 1 else 9
        for w in range(W+1):
            for k in range(0, min(w, 40)+1):            # k words in this phrase (0 = noise blip)
                p = dp[s-1][w-k]
                if p >= INF: continue
                n = cum[w] - cum[w-k]
                if k == 0: c = 6 + seg["nuc"]*.5 * (seg["end"]-seg["start"] > .3)
                else:
                    c = (n - seg["nuc"])**2 / (seg["nuc"] + 2)
                    # a pause before this phrase should coincide with a sentence/comma boundary
                    prev = words[w-k-1] if w-k > 0 else None
                    if prev is not None:
                        if gap > .55 and not (prev["send"] or prev["comma"]): c += 6
                        if prev["send"] and gap < .25: c += 3
                c += 0
                if p + c < dp[s][w]: dp[s][w] = p + c; bk[s][w] = k
    # backtrack
    groups, w = [], W
    for s in range(S, 0, -1):
        k = bk[s][w]; groups.append((s-1, w-k, w)); w -= k
    groups.reverse()
    for si, a, b in groups:
        if b == a: continue
        seg = segs[si]; n = cum[b] - cum[a]; d = seg["end"] - seg["start"]
        t = seg["start"]
        for i in range(a, b):
            ws = d * (cum[i] - cum[a]) / n; we = d * (cum[i+1] - cum[a]) / n
            words[i]["start"] = round(seg["start"] + ws, 3); words[i]["end"] = round(seg["start"] + we, 3)
    return words, groups

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("audio"); ap.add_argument("script"); ap.add_argument("-o", default="words.json")
    a = ap.parse_args()
    x, sr = load(a.audio); segs = phrases(x, sr)
    sents = [l.strip() for l in open(a.script) if l.strip()]
    words, groups = align(segs, sents)
    json.dump({"segments": segs, "words": words}, open(a.o, "w"), indent=1, ensure_ascii=False)
    print("segments", len(segs), "words", len(words), "syllables expected", sum(w["syl"] for w in words), "nuclei detected", sum(s["nuc"] for s in segs))


# ---- v2: sentence-constrained alignment (more robust; use this) -------------------------------------------
def align_in_sentences(segs, sentences, windows):
    """windows[i] = (start, end) of sentence i in the audio. Words are fitted to the acoustic phrases inside
    the window so each phrase gets a share of the sentence's syllables proportional to its duration."""
    out = []
    for si, (sent, (ws, we)) in enumerate(zip(sentences, windows)):
        toks = sent.split(); syls = [syl(t) for t in toks]; tot = sum(syls)
        sg = [s for s in segs if ws - .05 <= (s["start"] + s["end"]) / 2 <= we + .05]
        D = sum(s["end"] - s["start"] for s in sg) or 1
        cum = np.concatenate([[0], np.cumsum(syls)]); W = len(toks); S = len(sg)
        INF = 1e18; dp = np.full((S+1, W+1), INF); bk = np.zeros((S+1, W+1), int); dp[0][0] = 0
        for s in range(1, S+1):
            seg = sg[s-1]; d = seg["end"] - seg["start"]; gap = seg["start"] - sg[s-2]["end"] if s > 1 else 0
            for w in range(W+1):
                for k in range(0, w+1):
                    p = dp[s-1][w-k]
                    if p >= INF: continue
                    if k == 0: c = 0.25 if d < .2 else 3.0
                    else:
                        c = 100 * ((cum[w]-cum[w-k]) / tot - d / D) ** 2
                        if w-k > 0 and gap >= .25 and not toks[w-k-1].endswith((",", ":", "?", "!", ".")): c += .6
                    if p + c < dp[s][w]: dp[s][w] = p + c; bk[s][w] = k
        w, groups = W, []
        for s in range(S, 0, -1):
            k = bk[s][w]; groups.append((sg[s-1], w-k, w)); w -= k
        for seg, a, b in reversed(groups):
            if b == a: continue
            d = seg["end"] - seg["start"]; n = cum[b] - cum[a]
            for i in range(a, b):
                out.append({"w": toks[i], "sent": si, "start": round(seg["start"] + d*(cum[i]-cum[a])/n, 3),
                            "end": round(seg["start"] + d*(cum[i+1]-cum[a])/n, 3), "seg": (round(seg["start"],2), round(seg["end"],2))})
    return out

def to_chunks(words, max_words=3, hold_gap=.4):
    """Group aligned words into on-screen caption chunks: never cross a phrase pause; <= max_words each."""
    chunks, cur = [], []
    def flush():
        if cur: chunks.append([cur[0]["start"], cur[-1]["end"], " ".join(w["w"] for w in cur)])
    for w in words:
        if cur and (w["seg"] != cur[-1]["seg"] or len(cur) >= max_words): flush(); cur = []
        cur.append(w)
    flush()
    # even out chunk sizes within a phrase (avoid 3+1 splits) is skipped; keep each chunk until the next starts
    for i, c in enumerate(chunks):
        nxt = chunks[i+1][0] if i+1 < len(chunks) else c[1] + .3
        c[1] = round(min(nxt - .02, c[1] + (hold_gap if nxt - c[1] > hold_gap else nxt - c[1])), 3)
    return chunks
