#!/usr/bin/env bash
# Render completo: fotogramas -> efectos + música -> mezcla con la voz -> MP4 final + hoja de contactos.
set -euo pipefail
cd "$(dirname "$0")"
export NODE_PATH="${NODE_PATH:-$(npm root -g)}"
VOICE="${VOICE:-audio_in/voz.mp3}"

[ "${SKIP_FRAMES:-0}" = 1 ] || node render.js frames
python3 sfx.py
python3 music.py

# Mezcla: voz delante; la música baja sola cuando habla la voz (sidechain); efectos encima.
# Volumen final normalizado a -14 LUFS (estándar de Instagram/Reels).
ffmpeg -y -loglevel error -framerate 30 -i out/frames/%05d.png -i "$VOICE" -i out/music.wav -i out/sfx.wav \
  -filter_complex "\
[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=whole_dur=45,asplit=2[v][vk];\
[2:a]volume=0.32[m];[m][vk]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=400[md];\
[3:a]volume=0.8[s];\
[v][md][s]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -t 45 -movflags +faststart out/reel_tienda_confianza.mp4

# Hoja de contactos con fotogramas clave de cada escena
mkdir -p out/stills && rm -f out/stills/*.png
for t in 1.2 3.2 5.0 7.0 9.6 11.4 13.4 15.6 18.7 19.9 21.2 23.0 24.4 26.3 28.4 31.4 32.8 34.4 37.4 38.6 40.0 41.4 42.4 44.5; do
  f=$(printf "%05d" "$(python3 -c "print(round($t*30))")")
  cp "out/frames/$f.png" "out/stills/t_$t.png"
done
python3 contact_sheet.py out/hoja_contactos.png out/stills/*.png

ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate:format=duration -of compact out/reel_tienda_confianza.mp4
