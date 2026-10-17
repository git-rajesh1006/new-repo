# Remotion version (Day 6)

React/SVG motion graphics rendered with Remotion; every animation and the karaoke captions are keyed to the
spoken words via `video/day6-sync.json` (forced alignment from `video/align_voiceover.py`).

```
cd video/remotion
npm install
node render.mjs still 40.6 out/frame.png     # one frame
node render.mjs stills "10.9,40.6" out        # several frames
node render.mjs video out/day6.mp4           # full render (≈2 min)
npm run studio                               # live preview
```
`render.mjs` uses the Playwright headless-shell build at `/opt/pw-browsers/...` (set `CHROME_PATH` to override).
To use new audio/timings: copy the new mp3 to `public/day6-voiceover.mp3` and the new sync JSON to `src/day6-sync.json`.
