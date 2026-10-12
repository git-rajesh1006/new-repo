"""Align script_lines.txt to a voiceover and write everything the video needs:
captions.json (caption chunks), cues.json + anim/assets/cues.js (scene boundaries and animation cues).
Usage: python build_cues.py <audio> <windows.json>   (windows = [[start,end],...] one per script sentence)"""
import sys, json, re
sys.path.insert(0, "../../tools")
import align
audio, wfile = sys.argv[1], sys.argv[2]
x, sr = align.load(audio); dur = round(len(x) / sr, 2); segs = align.phrases(x, sr)
sents = [l.strip() for l in open("script_lines.txt") if l.strip()]
win = json.load(open(wfile)); assert len(win) == len(sents), (len(win), len(sents))
words = align.align_in_sentences(segs, sents, win)
chunks = align.to_chunks(words)
json.dump({"words": words, "chunks": chunks}, open("captions.json", "w"), indent=1, ensure_ascii=False)
clean = lambda w: re.sub(r"[^\w/]", "", w).lower()
def W(si, tok, nth=0):
    m = [w for w in words if w["sent"] == si and clean(w["w"]) == clean(tok)]
    return m[nth]["start"]
first = lambda si: min(w["start"] for w in words if w["sent"] == si)
last = lambda si: max(w["end"] for w in words if w["sent"] == si)
groups = [[0], [1, 2, 3], [4, 5, 6], [7, 8], [9, 10], [11, 12, 13]]       # hook, problem, solution, example, takeaway, CTA
S = [0.0] + [round((last(g[-1]) + first(groups[i+1][0])) / 2, 2) for i, g in enumerate(groups[:-1])] + [dur]
T = {
 "box": S[1] + .2, "s2t": S[1] + .6, "appIn": S[1] + 1.0, "appMove": W(2, "deploy") - .2, "appRed": W(2, "errors"),
 "e1": W(2, "errors"), "e2": W(2, "errors") + .7, "e3": W(3, "Operations"), "e4": W(3, "coordination"),
 "boxes3": S[2] + .3, "merge": W(4, "DevOps") - .3, "devops": W(4, "DevOps") + .7,
 "collab": W(5, "Development"), "auto": W(5, "Operations"), "goal": W(6, "fast"),
 "n1": W(7, "GitHub") - .2, "term": S[3] + .3, "t0": W(7, "push"), "n2": W(8, "pipeline"), "t1": W(8, "automatic"),
 "n3": W(8, "test"), "t2": W(8, "test") + .4, "n4": W(8, "deploy"), "t3": W(8, "deploy") + .5,
 "tools": S[4] + .4, "devops5": W(9, "tools") + .2, "p1": W(10, "Automation"), "p2": W(10, "collaboration"), "p3": W(10, "continuous"),
 "c1": S[5] + .2, "c2": S[5] + .6, "day1": W(11, "Day"), "next": W(12, "Day"), "nextEng": W(12, "DevOps"), "follow": W(13, "Follow"),
}
T = {k: round(v, 2) for k, v in T.items()}
for k in ("n1","n2","n3","n4"): assert T[k] > 0
out = {"dur": dur, "S": S, "T": T, "errs": [T["e1"], T["e2"], T["e3"], T["e4"]], "pings": [T["t2"], T["t3"]], "slam": T["day1"]}
json.dump(out, open("cues.json", "w"), indent=1)
open("anim/assets/cues.js", "w").write("window.CUE = " + json.dumps(out) + ";\n")
print("dur", dur, "scenes", S); print(T)
