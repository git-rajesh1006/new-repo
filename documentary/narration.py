"""Narration segments (from the supplied script) + offline English TTS fitted to each scene window."""
import ctypes, numpy as np, espeakng_loader

SEGMENTS = [  # (scene_start, scene_end, text)
 (0, 15, "My team took two to three days to make a YouTube intro. What if an AI could make its version in just forty minutes?"),
 (15, 28, "That’s the claim I wanted to put to the test with Claude Opus 5.5."),
 (28, 42, "And here’s the surprising part: in this workflow, it appeared to identify and organize takes without listening to a single word I said."),
 (42, 58, "In this video, I’m testing real creative tasks and comparing the workflow with ChatGPT 6 Astra. The goal isn’t hype. It’s to see what actually gets done."),
 (58, 75, "We’ll go from raw talking-head footage to a YouTube intro, test take selection, build motion graphics with code, recreate a team-made intro, and make a SaaS promo from scratch. Then we’ll look at sound design, render time, usage, and what this means for editors."),
 (75, 100, "First, the raw footage. The workflow is familiar: organize the clips, choose the strongest moments, build a sequence, add titles and motion, then export. The question is how much of that process the model can meaningfully accelerate."),
 (100, 125, "Next, take selection. Instead of manually reviewing every repeated take, the system organizes the material and proposes a cleaner sequence. That can save time—but the final cut still needs a human check for meaning, timing, and natural delivery."),
 (125, 148, "The interesting part is that the video can be described through code. Timing, shapes, typography, and transitions become instructions that generate motion. That makes iteration powerful, especially for graphics that would otherwise take repeated manual adjustments."),
 (148, 170, "Now the harder test: recreating an intro made by a motion design team. Matching the reference means more than copying colors. Composition, rhythm, typography, and the feeling of each transition all matter."),
 (170, 200, "Then I asked it to create a SaaS promo from scratch. The goal is a clear product story: show the interface, communicate the benefit, and finish with a call to action. Strong motion design should make the message easier to understand—not just make the screen look busy."),
 (200, 220, "Sound is what makes these graphics feel finished. Music gives the piece momentum, while clicks, whooshes, and impacts emphasize important actions. The mix has to leave space for narration, so the music ducks whenever the voice needs to lead."),
 (220, 240, "There’s also the practical side: setup, render time, and usage limits. These depend on the project, settings, and plan, so it’s worth measuring them instead of assuming every job will be equally fast."),
 (240, 265, "So how does Claude Opus 5.5 compare with ChatGPT 6 Astra? The useful answer comes from the actual task: which one follows the brief, produces editable results, handles revisions, and fits the tools you already use? One test isn’t a universal leaderboard—but it can reveal which workflow suits your work."),
 (265, 285, "For editors and motion designers, the biggest opportunity may be less repetitive work and faster first drafts. That leaves more time for story, taste, pacing, and the details that make a video feel intentional."),
 (285, 298, "AI can accelerate the workflow. But direction, judgment, and the final creative decisions still matter."),
 (298, 300, "The future of video creation isn’t just human. It’s AI plus human."),
]

_lib = ctypes.CDLL(espeakng_loader.get_library_path())
SR = _lib.espeak_Initialize(2, 0, espeakng_loader.get_data_path().encode(), 0)
_buf = []
CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)
@CB
def _cb(w, n, ev):
    if w and n > 0: _buf.append(np.ctypeslib.as_array(w, (n,)).copy())
    return 0
_lib.espeak_SetSynthCallback(_cb)
assert _lib.espeak_SetVoiceByName(b"en-us") == 0

def speak(text, rate, pitch=42):
    _lib.espeak_SetParameter(1, int(rate), 0); _lib.espeak_SetParameter(3, pitch, 0)
    _lib.espeak_SetParameter(2, 100, 0)
    _buf.clear(); b = text.encode(); _lib.espeak_Synth(b, len(b) + 1, 0, 1, 0, 1, None, None); _lib.espeak_Synchronize()
    return np.concatenate(_buf).astype(np.float32) / 32768.0

def fit(text, window, lo=110, hi=320):
    """Pick the slowest speaking rate whose audio still fits `window` seconds."""
    best = None
    for _ in range(9):
        mid = (lo + hi) / 2; a = speak(text, mid)
        if len(a) / SR <= window: best, hi = (mid, a), mid
        else: lo = mid
    if best is None: best = (hi, speak(text, hi))
    return best
