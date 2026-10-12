# Series conventions (100 Days of DevOps)

## Voiceover script = the on-screen captions (rule from the creator)
When asked for a voiceover, always give the **exact caption text shown in the video**, in order, one caption per line
(with its timestamp). Never write a separate "voiceover" version that differs from the captions.

How to keep them identical:
- One source of truth per episode: `episodes/dayNN/script_lines.txt` (one sentence per line).
- The captions in the video are generated from that file (`tools/align.py` -> `captions.json`), and
  the voiceover handed to the creator is printed from the same text/chunks — nothing is re-worded in between.
- If the creator changes any words while recording, they say so (or paste what they said) and the captions are
  regenerated from the spoken words, not the other way round.
