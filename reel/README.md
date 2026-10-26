# Reel · "Tu tienda no da confianza" (@joaquinperez.ecom)

Reel vertical de 45 s (1080×1920, 30 fps, H.264 + AAC), hecho como animación HTML con una línea de tiempo determinista.

## Archivos entregados (`out/`)
- `reel_tienda_confianza.mp4`: vídeo final con voz, música de fondo y efectos de sonido (−14 LUFS).
- `hoja_contactos.png`: fotogramas clave de cada escena. Las líneas rojas discontinuas marcan la zona segura (250 px arriba, 340 px abajo).

## Audio
- **Voz** (`audio_in/voz.mp3`): locución generada con vidIQ (voz "Chris"). Las escenas (objeto `T` en `index.html`) están sincronizadas con las pausas de esta voz.
- **Música** (`music.py`): base original sintetizada a 96 BPM, sin derechos de terceros. Se corta en seco en "¿Tú compras ahí?" y gana brillo en la solución. Baja sola cuando habla la voz.
- **Efectos** (`sfx.py`): swoosh, pop, golpe seco, ding de check, tictac del contador, pasos, puerta y teclas, colocados en cada animación.

## Código
- `index.html`: la animación. `render(t)` dibuja el estado en el segundo `t`. Ábrelo en el navegador para ver una vista previa (sin sonido).
- `render.js`: renderiza los fotogramas con Playwright + Chromium y exporta `out/cues.json` (los tiempos de los efectos).
- `contact_sheet.py`: genera la hoja de contactos.
- `build.sh`: lo ejecuta todo y hace la mezcla final (unos 2 minutos).

## Cómo exportar
```bash
npm i -g playwright          # Chromium incluido: npx playwright install chromium
pip install numpy scipy pillow   # además de ffmpeg
./build.sh                   # SKIP_FRAMES=1 ./build.sh reutiliza los fotogramas ya renderizados
```

## Usar tu propia voz
Graba el guion y ejecuta `VOICE=mi_voz.wav ./build.sh`. Si tu ritmo es distinto, ajusta los valores de `T` en `index.html` a tus pausas.
Para ver dónde hay pausas: `ffmpeg -i mi_voz.wav -af silencedetect=noise=-35dB:d=0.12 -f null -`.

## Prueba social (opcional)
Si pones `assets/tienda.png`, se activa una escena con tu captura justo antes de la llamada a la acción.
La voz actual no incluye la frase "Es lo primero que miro en mis tiendas": añádela si activas la escena.
