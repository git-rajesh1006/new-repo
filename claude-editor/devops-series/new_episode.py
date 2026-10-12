"""Scaffold a day: python new_episode.py <day>  ->  episodes/dayNN/{brief.md,script.md}"""
import json, sys
from pathlib import Path
d = int(sys.argv[1]); s = json.load(open(Path(__file__).parent / "syllabus.json"))
day = next(x for x in s["days"] if x["day"] == d)
out = Path(__file__).parent / "episodes" / f"day{d:02d}"; out.mkdir(parents=True, exist_ok=True)
(out / "brief.md").write_text(f"# Day {d} — {day['title']}\n{day['phase']}\n\nAspect 9:16, 30-60s. One file for Reel + Short.\nVoiceover file: voiceover.(wav|mp3|m4a|mp4)\nStyle: dark terminal, romanized Tenglish captions.\n")
beats = "\n".join(f"## {b['name']} ({b['start']}-{b['end']}s)\n{b['note']}\nTenglish script:\n\n" for b in s["reel_format"])
(out / "script.md").write_text(f"# Day {d} script — {day['title']}\n\n{beats}")
print(out)
