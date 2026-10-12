# Tenglish narration script (35 s vertical ad)

Generate each clip as a separate file (01.mp3 … 12.mp3). Keep each clip inside its time window — I speed it up slightly (max 1.4×) if it runs long.

| # | Start | Window | Say this (Tenglish) |
|---|---|---|---|
| 01 | 0.0s | 4.0s | Ippudu Claude mee YouTube channel antha run chestundi... aa kuda, completely free. |
| 02 | 4.0s | 2.3s | Daani peru, YouTube Agent Skill. |
| 03 | 6.3s | 2.3s | Idi okka skill kaadu. Eleven skills. |
| 04 | 8.6s | 3.1s | Okkati, mee scripts raastundi... twenty-one proven hook formulas tho. |
| 05 | 11.7s | 2.0s | Inkokati, titles and thumbnails chestundi. |
| 06 | 13.7s | 1.0s | Inkokati, mee videos edit chestundi. |
| 07 | 14.7s | 1.3s | Inkokati, comments ki reply istundi. |
| 08 | 15.9s | 2.1s | Inka okati, mee whole strategy plan chestundi. |
| 09 | 18.0s | 9.0s | Kaani asalu crazy ayyindi? Virality. Mee niche lo most viral videos ni kanipettesi, avi exactly enduku work ayyayo break down chesi, mee voice lo, mee audience kosam malli rebuild chestundi. |
| 10 | 27.0s | 1.3s | Ika em post cheyalo guess cheyalsina pani ledu. |
| 11 | 28.3s | 3.7s | Setup ki ten seconds chalu. Claude open chesi, oka link paste cheyandi, done. |
| 12 | 32.0s | 3.0s | YOUTUBE ani comment cheyandi, nenu meeku full guide DM chestanu. |

**ElevenLabs tips:** Multilingual v2, Stability ~45%, Similarity ~75%, speed 1.0–1.1. Say numbers as words (already written out). Use a voice that handles Indian-English / Telugu names naturally.

**Then run:** `python3 build.py out.mp4 --voice clips_dir/` (12 files) or `--voice one_file.mp3` (one file, 12 clips separated by pauses of ~1 s).
