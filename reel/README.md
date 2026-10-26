# Reel · "Tu tienda no da confianza" (@joaquinperez.ecom)

Reel vertical de 45 s (1080×1920, 30 fps, H.264 + AAC), hecho como animación HTML con una línea de tiempo determinista.

## Archivos entregados (`out/`)
- `reel_tienda_confianza.mp4`: vídeo final con efectos de sonido sintetizados (sin voz ni música).
- `reel_tienda_confianza_GUIA_tiempos.mp4`: copia con código de tiempo, escena y frase de voz, para grabar la voz encima.
- `hoja_contactos.png`: fotogramas clave de cada escena. Las líneas rojas discontinuas marcan la zona segura (250 px arriba, 340 px abajo).

## Código
- `index.html`: la animación. `render(t)` dibuja el estado en el segundo `t`. Los tiempos de cada escena están en el objeto `T`, arriba del script.
  Ábrelo en el navegador para ver una vista previa en tiempo real.
- `render.js`: renderiza los fotogramas con Playwright + Chromium y exporta `out/cues.json` (los efectos de sonido).
- `sfx.py`: sintetiza los efectos (swoosh, pop, golpe seco, ding, tick, tecla) con NumPy.
- `make_guide.py`: genera los rótulos de la copia guía.
- `contact_sheet.py`: genera la hoja de contactos.
- `build.sh`: lo ejecuta todo (unos 2 minutos).

## Cómo exportar
```bash
npm i -g playwright          # Chromium incluido: npx playwright install chromium
pip install numpy pillow     # además de ffmpeg
./build.sh                   # SKIP_FRAMES=1 ./build.sh reutiliza los fotogramas ya renderizados
```

## Prueba social (escena opcional 34–37 s)
Pon tu captura en `assets/tienda.png` (vertical, mejor 9:19) y vuelve a ejecutar `./build.sh`.
La escena se activa sola y la de solución se acorta hasta 34 s.

## Sincronizar con tu voz
Ajusta los valores de `T` en `index.html` a tu grabación. Después mezcla tu voz con los efectos, por ejemplo:
```bash
ffmpeg -i out/reel_tienda_confianza.mp4 -i voz.wav -filter_complex "[0:a]volume=0.6[s];[1:a][s]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart out/reel_con_voz.mp4
```
