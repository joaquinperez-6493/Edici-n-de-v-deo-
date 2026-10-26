"""Hoja de contactos: miniaturas de fotogramas clave con la zona segura marcada.

Uso: python3 contact_sheet.py salida.png out/stills/t_1.00.png ...
(El nombre del archivo t_<segundos>.png se usa como etiqueta.)
"""
import re
import sys

from PIL import Image, ImageDraw, ImageFont

COLS, TW, TH, PAD, LABEL = 6, 300, 533, 18, 46
SAFE_TOP, SAFE_BOTTOM = 250, 340
FONT = "fonts/InterDisplay-SemiBold.otf"


def main(out, files):
    files = sorted(files, key=lambda f: float(re.search(r"t_([\d.]+)\.png", f).group(1)))
    rows = (len(files) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * (TW + PAD) + PAD, rows * (TH + LABEL + PAD) + PAD), "#1d2224")
    font = ImageFont.truetype(FONT, 26)
    k = TW / 1080
    for i, f in enumerate(files):
        t = float(re.search(r"t_([\d.]+)\.png", f).group(1))
        im = Image.open(f).convert("RGB").resize((TW, TH), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        for y in (SAFE_TOP * k, TH - SAFE_BOTTOM * k):  # límites de zona segura
            for x in range(0, TW, 10):
                d.line([(x, y), (x + 5, y)], fill="#ff3b30", width=1)
        x0 = PAD + (i % COLS) * (TW + PAD)
        y0 = PAD + (i // COLS) * (TH + LABEL + PAD)
        sheet.paste(im, (x0, y0 + LABEL))
        ImageDraw.Draw(sheet).text((x0 + 4, y0 + 8), f"{int(t // 60):02d}:{t % 60:05.2f}", font=font, fill="#F4F6F2")
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
