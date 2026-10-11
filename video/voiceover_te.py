"""Add a Telugu voice-over to discipline_poor_kid.mp4 (re-muxes audio; video is copied untouched)."""
import sys, subprocess, wave, numpy as np
import make_video as mv, tts_te

LINES = [  # (start, latest_end, text)
    (0.85, 2.15, "ఈ కథ ఇలా ముగుస్తుంది."),
    (2.40, 4.25, "కానీ ఇది ఇక్కడే మొదలైంది."),
    (4.40, 6.00, "మొదటి రోజు. లేస్తాడా?"),
    (6.40, 10.40, "రేపు చూద్దాం అనుకున్నాడు."),
    (10.90, 15.30, "నలభై ఏడో రోజు. ఎందుకు ప్రయత్నించడం? అని ఆ గొంతు అంది."),
    (15.80, 19.30, "నూట యాభై రోజులు. అలారం మోగింది. అతను లేవలేదు."),
    (19.80, 23.30, "మూడు వందల అరవై ఐదు రోజులు. మరో సంవత్సరం గడిచిపోయింది."),
    (24.30, 27.90, "నువ్వు సోమరివి అని ఆ గొంతు అంది."),
    (28.20, 29.90, "అతను నమ్మేశాడు."),
    (30.10, 32.40, "కానీ సోమరితనం నీ నిజ స్వరూపం కాదు."),
    (34.15, 35.40, "చాలు."),
    (35.80, 38.90, "మొదటి రోజు. ఈసారి నిజంగా."),
    (39.20, 43.90, "మూడో రోజు. చెప్పులు లేవు. కడుపులో ఆకలి. అయినా పరుగు ఆపలేదు."),
    (44.20, 48.40, "పన్నెండో రోజు. కేవలం ఐదు పుష్ అప్స్."),
    (48.70, 52.90, "అరవై నాలుగో రోజు. ఎవరికీ పట్టదు అన్నారు. అయినా కొట్టాడు."),
    (53.80, 57.40, "నూట యాభై రోజులు. ప్రతి రోజూ, చప్పట్లు లేకపోయినా."),
    (57.70, 61.90, "ప్రేరణ నిన్ను మొదలుపెట్టిస్తుంది."),
    (62.00, 65.00, "క్రమశిక్షణ నిన్ను నడిపిస్తుంది."),
    (65.30, 68.90, "నిన్ను కాపాడటానికి ఎవరూ రారు."),
    (69.10, 71.00, "కాబట్టి నిన్ను నువ్వే కాపాడుకో."),
    (71.40, 74.80, "రేపటి కోసం అతను ఆగలేదు."),
    (76.20, 77.80, "ఈ రోజే, లేక ఎప్పుడో?"),
    (78.10, 79.80, "నిర్ణయం నీదే."),
]

def build_voice():
    sr = mv.SR; n = int(mv.TOTAL * sr); voice = np.zeros(n, np.float32)
    for k, (start, end, text) in enumerate(LINES):
        nxt = LINES[k + 1][0] if k + 1 < len(LINES) else mv.TOTAL
        end = min(end + 0.6, nxt - 0.15)   # let a line bleed slightly into the next scene
        rate = 110
        while True:
            a = tts_te.speak(text, rate=rate)
            dur = len(a) / tts_te.SR
            if start + dur <= end or rate >= 175: break
            rate = int(rate * 1.1) + 1
        a = np.interp(np.arange(int(dur * sr)) / sr, np.arange(len(a)) / tts_te.SR, a).astype(np.float32)
        i = int(start * sr); j = min(n, i + len(a)); voice[i:j] += a[:j - i]
        print(f"{start:5.1f}s rate={rate:3d} dur={dur:4.2f}/{end - start:4.2f}  {text}")
    peak = np.abs(voice).max(); return voice / peak * 0.95 if peak else voice

def main(src, dst):
    music = mv.synth(); voice = build_voice()
    # duck the music while the narrator speaks
    env = np.convolve(np.abs(voice) > 0.02, np.ones(int(0.25 * mv.SR)) / int(0.25 * mv.SR), "same")
    duck = 1 - 0.55 * np.clip(env * 4, 0, 1)
    mix = np.tanh(music * duck * 0.9 + voice * 1.1); mix /= np.abs(mix).max() / 0.92
    wavp = dst + ".wav"
    with wave.open(wavp, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(mv.SR)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", wavp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", dst], check=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
