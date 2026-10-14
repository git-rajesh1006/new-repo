"""Forced-align every phrase of day3_phrases.py against the voiceover with pocketsphinx and write
day3-sync.json: [{"a","b","text","times":[start per script token]}].
Usage: python3 align_voiceover.py voiceover.mp3 day3-sync.json   (needs pocketsphinx, ffmpeg)
Telugu words get a rule-based pronunciation; the alignment is per phrase, so a few tenths of
a second of error at most, and each phrase is clamped inside its measured speech window."""
import json, re, subprocess, sys, tempfile, wave
from pocketsphinx import Decoder, Config, get_model_path
from day3_phrases import PHRASES

SPOKEN = {"100": "one hundred", "3": "three", "2": "two", "4": "four", "devops": "devops"}
EXTRA = {"devops": "D EH V AA P S", "lifecycle": "L AY F S AY K AH L"}
M = {'ch': ['CH'], 'th': ['T', 'HH'], 'sh': ['SH'], 'kh': ['K', 'HH'], 'dh': ['D', 'HH'], 'ee': ['IY'], 'oo': ['UW'], 'ai': ['AY'], 'au': ['AW'], 'aa': ['AA']}
C = {'b': 'B', 'c': 'K', 'd': 'D', 'f': 'F', 'g': 'G', 'h': 'HH', 'j': 'JH', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'p': 'P', 'q': 'K', 'r': 'R', 's': 'S', 't': 'T', 'v': 'V', 'w': 'W', 'x': 'K S', 'y': 'Y', 'z': 'Z'}
V = {'a': 'AA', 'e': 'EH', 'i': 'IH', 'o': 'OW', 'u': 'UH'}
def g2p(word):
    s, out, i = word.lower(), [], 0
    while i < len(s):
        if s[i:i + 2] in M: out += M[s[i:i + 2]]; i += 2; continue
        ch = s[i]
        if ch in V: out.append(V[ch])
        elif ch in C: out += C[ch].split()
        i += 1
    return out

def clean(w): return re.sub(r"[^A-Za-z0-9']", "", w)

def main(audio, out):
    with tempfile.TemporaryDirectory() as td:
        wav = td + "/a.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio, "-ac", "1", "-ar", "16000", wav], check=True)
        w = wave.open(wav); pcm = w.readframes(w.getnframes())
    sr, mp = 16000, get_model_path()
    dec = Decoder(Config(hmm=mp + "/en-us/en-us", dict=mp + "/en-us/cmudict-en-us.dict", loglevel="FATAL"))
    res, added = [], set()
    for a, b, text in PHRASES:
        toks = text.split()
        spoken, owner = [], []          # spoken words and which script token each belongs to
        for ti, tk in enumerate(toks):
            c = clean(tk).lower()
            for sw in SPOKEN.get(c, c).split():
                spoken.append(sw); owner.append(ti)
        for sw in set(spoken):
            if dec.lookup_word(sw) is None or sw in EXTRA and sw not in added:
                if dec.lookup_word(sw) is None: dec.add_word(sw, EXTRA.get(sw) or " ".join(g2p(sw)), update=False)
                added.add(sw)
        times, ok = [None] * len(toks), True
        try:
            dec.set_align_text(" ".join(spoken))
            dec.start_utt(); dec.process_raw(pcm[int((a - .05) * sr) * 2:int((b + .05) * sr) * 2], full_utt=True); dec.end_utt()
            segs = [s for s in dec.seg() if not s.word.startswith("<") and s.word != "(NULL)"]
            assert len(segs) == len(spoken)
            for sg, ti in zip(segs, owner):
                st = a - .05 + sg.start_frame / 100
                if times[ti] is None: times[ti] = st
        except Exception as e:
            ok = False
        if not ok:      # fall back to letter-proportional timing inside the window
            tot = sum(len(clean(t)) + 1 for t in toks); acc = 0
            for i, t in enumerate(toks):
                times[i] = a + (b - a) * acc / tot; acc += len(clean(t)) + 1
        times = [min(max(t, a), b) for t in times]
        for i in range(1, len(times)): times[i] = max(times[i], times[i - 1] + .03)
        res.append(dict(a=a, b=b, text=text, times=times, aligned=ok))
    json.dump(res, open(out, "w"), indent=1)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
