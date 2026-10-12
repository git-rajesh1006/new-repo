# Publishing process — 100 Days of DevOps (Telugu)

One video file per day (`dayNN_final*.mp4`, 9:16). Upload it to **YouTube Shorts** and **Instagram Reels** separately,
each with its own title/caption, thumbnail/cover and keywords. Per-episode metadata lives in `episodes/dayNN/publish.md`
(generate with `python tools/publish_meta.py <day>`).

Platform UIs change often; treat the steps below as the shape of the flow, not exact button names.

## Before uploading (both platforms)
- [ ] Play the final video once, with sound, start to end (captions match voice, no clipped audio, loudness comfortable).
- [ ] File: MP4 (H.264 + AAC), 1080x1920, under 3 minutes. No watermark from other apps.
- [ ] Keep key text/faces in the centre; the bottom ~20% and the right edge are covered by each app's UI.
- [ ] Thumbnail/cover ready: `thumbs/reel_cover_1080x1920.png` (9:16) and `thumbs/youtube_thumb_1280x720.png` (16:9).
- [ ] Disclosure: this series uses a synthetic (text-to-speech) voice and generated music. Answer each platform's
      "altered or synthetic content / AI info" question honestly (see each section).

## A. YouTube Shorts  (desktop: studio.youtube.com)
1. **Create -> Upload videos**, select the MP4. A vertical video under 3 minutes is published as a Short automatically.
2. **Title** (<= 100 chars, first ~60 are what people see). Pattern: `<Topic in Telugu words> | <English topic> in Telugu | Day N`
3. **Description**: line 1-2 = what they'll learn + keywords (shown before "more"); then series link/playlist, chapters not needed for Shorts;
   put 3-5 hashtags at the end (the first 3 appear above the title; more than 15 and YouTube ignores them all).
4. **Thumbnail**: upload the custom image if the option is shown for the Short (on some accounts/apps Shorts only let you pick a frame).
   If you can only pick a frame, choose the opening frame ("WHAT IS DEVOPS?") — it is the designed hook frame.
5. **Playlist**: add to "100 Days of DevOps (Telugu)" (create it on Day 1).
6. **Audience**: "No, it's not made for kids". **Language**: Telugu. **Category**: Education.
7. **Tags** (Show more): low weight, but add the keyword list from `publish.md`.
8. **Disclosures**: answer the "altered or synthetic content" question. A clearly synthetic narrator that is not imitating a real person
   usually doesn't need the label, but read the current wording and answer honestly.
9. **Visibility**: Schedule (same time daily) or Public. Add **pinned comment** after publishing (question + next-day teaser).
10. After 24-48 h: Studio -> Analytics -> check *Viewed vs swiped away* and average view duration; use it to rewrite hooks.

## B. Instagram Reels  (app, or Meta Business Suite on desktop for scheduling)
1. **+ -> Reel**, pick the MP4 from the gallery (or upload via Meta Business Suite / instagram.com on desktop).
2. **Edit cover -> Add from camera roll**, pick `reel_cover_1080x1920.png`. Keep text in the centre: the profile grid crops the cover.
3. **Caption**: first line is the hook (it is the only line visible before "more"), include the topic keywords in plain words, a question
   to drive comments, then **3-5 hashtags** (more doesn't help).
4. **Alt text / accessibility** (Advanced settings): one sentence describing the video, with the keywords.
5. **Audio**: leave as "Original audio" (the mixed voice+music track).
6. **Share to feed**: on. **Also share to Facebook**: optional.
7. **AI label**: if the app asks, answer the "AI info"/"made with AI" question honestly (synthetic voice/music).
8. **Schedule** (professional account via Meta Business Suite) or post now. Reply to the first comments within the first hour.
9. After 24-48 h: Insights -> reach, plays, average watch time, shares/saves; shares and saves matter most.

## Titles / keywords cheat-sheet
- Mix **Telugu script** (what Telugu speakers type) and **English/Roman** (what they also search): e.g. `DevOps అంటే ఏమిటి?` + `devops in telugu`.
- Always include: `devops in telugu`, `<topic> in telugu`, `devops for beginners`, `100 days of devops`.
- Keep the Day number in every title: viewers binge by number.
- Don't stuff: 3-5 hashtags, relevant tags only.

## Daily routine (~10 minutes after the video is rendered)
1. `python tools/publish_meta.py <day>` -> edit title/hook if needed.
2. YouTube Studio upload (section A). 3. Instagram upload (section B). 4. Pin comment + reply to early comments.
5. Next morning: note views/retention in `episodes/dayNN/publish.md` (Results section) to learn what hooks work.
