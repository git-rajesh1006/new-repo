#!/usr/bin/env bash
# Voice modulation + music/SFX mix. Usage: ./mix.sh <voiceover> <video_in> <video_out> <dur> [pitch]
set -euo pipefail
cd "$(dirname "$0")/.."   # run from the episode folder so intermediate files land there
VO="$1"; VIN="$2"; VOUT="$3"; DUR="$4"; PITCH="${5:-0.92}"; SPEED="${6:-1.0}"; ODUR=$(awk "BEGIN{printf \"%.2f\", $DUR/$SPEED}")
# 1) Modulated voice: pitch down ~1.4 semitones with formant shift, warmth + presence EQ,
#    gentle compression, subtle doubler for a fuller "narrator" tone. Duration is unchanged.
ffmpeg -y -v error -i "$VO" -af "volume=-4dB,highpass=f=85,rubberband=tempo=$SPEED:pitch=$PITCH:formant=shifted,\
equalizer=f=140:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1:g=2.5,equalizer=f=7500:t=q:w=2:g=-2,\
acompressor=threshold=-20dB:ratio=3:attack=8:release=140:makeup=4,\
asplit[a][b];[b]adelay=22|22,volume=-13dB,highpass=f=300[c];[a][c]amix=inputs=2:normalize=0,aformat=sample_rates=48000:channel_layouts=stereo" voice_mod.wav
# 2) Mix: music ducks under the voice (sidechain), SFX on top, then master to -14 LUFS / -1 dBTP
ffmpeg -y -v error -i voice_mod.wav -i music.wav -i sfx.wav -i "$VIN" -filter_complex "\
[0:a]volume=-3dB,apad=whole_dur=$ODUR,asplit[vo][key];\
[1:a]atempo=$SPEED,volume=0.62[m];[m][key]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=450:makeup=1[md];\
[2:a]atempo=$SPEED,volume=0.55[fx];\
[vo][md][fx]amix=inputs=3:normalize=0:duration=longest,loudnorm=I=-14:TP=-1:LRA=9,atrim=0:$ODUR[mix]" \
-map 3:v -map "[mix]" -c:v copy -c:a aac -b:a 192k -shortest "$VOUT"
