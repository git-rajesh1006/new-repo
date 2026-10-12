"""Generate episodes/dayNN/publish.md (titles, descriptions, hashtags, keywords) from syllabus.json.
Usage: python tools/publish_meta.py <day>   (won't overwrite an existing file; pass --force)"""
import json, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]; day = int(sys.argv[1]); force = "--force" in sys.argv
d = next(x for x in json.load(open(root / "syllabus.json"))["days"] if x["day"] == day)
out = root / "episodes" / f"day{day:02d}" / "publish.md"
if out.exists() and not force: sys.exit(f"{out} exists (use --force)")
t = d["title"].rstrip("?"); tl = t.lower()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(f"""# Day {day} — publishing metadata
Topic: {d['title']}  ({d['phase']})

## YouTube Shorts
Title options (<= 100 chars):
1. {t} in Telugu | Day {day}/100 | 100 Days of DevOps
2. {t}? DevOps Telugu Tutorial | Day {day}
3. Day {day}: {t} (Telugu) #DevOps

Description:
{t} — simple Telugu (Tenglish) explanation with a real-world example. Day {day} of the 100 Days of DevOps series.
Follow for one DevOps video every day.

#DevOps #DevOpsInTelugu #100DaysOfDevOps #TeluguTech

Tags: {tl} in telugu, {tl}, devops in telugu, devops for beginners, learn devops telugu, 100 days of devops, devops tutorial telugu, telugu tech
Playlist: 100 Days of DevOps (Telugu) | Language: Telugu | Category: Education | Not made for kids
Pinned comment: "Day {day + 1} lo kalusukundam! Ee roju em nerchukunnaru? Comment lo cheppandi."

## Instagram Reels
Caption:
{t}? 👇 Simple ga Telugu lo — Day {day}/100.
Daily oka DevOps topic. Follow avvandi, save chesukondi.
Em doubts unnaayi? Comment lo adagandi!

#devops #devopsintelugu #telugutech #100daysofdevops #learndevops
Alt text: Telugu explanation of {tl}, Day {day} of 100 Days of DevOps.
Cover: thumbs/reel_cover_1080x1920.png

## Results (fill in 24-48 h after posting)
YouTube: views / avg view duration / viewed-vs-swiped:
Instagram: plays / avg watch time / shares / saves:
""")
print(out)
