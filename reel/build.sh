#!/usr/bin/env bash
# Render completo: fotogramas -> efectos de sonido -> MP4 final + copia guía + hoja de contactos.
set -euo pipefail
cd "$(dirname "$0")"
export NODE_PATH="${NODE_PATH:-$(npm root -g)}"

[ "${SKIP_FRAMES:-0}" = 1 ] || node render.js frames
python3 sfx.py
python3 make_guide.py

# MP4 final: H.264, yuv420p, 30 fps, audio AAC
ffmpeg -y -loglevel error -framerate 30 -i out/frames/%05d.png -i out/sfx.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -shortest -movflags +faststart out/reel_tienda_confianza.mp4

# Copia guía: código de tiempo + escena + frase de voz (para grabar encima)
ffmpeg -y -loglevel error -i out/reel_tienda_confianza.mp4 \
  -vf "subtitles=out/guide.ass:fontsdir=fonts,drawtext=fontfile=fonts/InterDisplay-SemiBold.otf:text='%{pts\:hms}':x=40:y=70:fontsize=40:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=12" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p -c:a copy -movflags +faststart out/reel_tienda_confianza_GUIA_tiempos.mp4

# Hoja de contactos con fotogramas clave de cada escena
mkdir -p out/stills && rm -f out/stills/*.png
for t in 1.0 2.4 3.6 4.4 6.2 9.0 12.4 14.0 15.6 17.0 18.4 19.6 21.0 23.0 24.6 27.2 31.2 34.5 37.6 39.4 41.0 44.5; do
  f=$(printf "%05d" "$(python3 -c "print(round($t*30))")")
  cp "out/frames/$f.png" "out/stills/t_$t.png"
done
python3 contact_sheet.py out/hoja_contactos.png out/stills/*.png

for f in out/reel_tienda_confianza.mp4 out/reel_tienda_confianza_GUIA_tiempos.mp4; do
  ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration -of compact "$f"
done
