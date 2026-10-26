"""Genera out/guide.ass: copia guía con escena y frase de voz para grabar encima.

Lee los tiempos reales de out/cues.json (los mismos que usa la animación).
"""
import json

info = json.load(open("out/cues.json"))
T, proof = info["times"], info["proof"]

LINES = [
    (0, 2.2, "1 · GANCHO", "Entran cien personas en tu tienda y ninguna compra."),
    (2.2, T["storeIn"], "1 · GANCHO", "Y tú piensas que te falta gente."),
    (T["storeIn"], T["doorOpen"] + 2.2, "2 · LA TIENDA", "A ver, imagínate que entras en una tienda de verdad."),
    (T["doorOpen"] + 2.2, T["bPrecios"], "2 · LA TIENDA", "No hay nadie."),
    (T["bPrecios"], T["bCartel"], "2 · LA TIENDA", "Ningún precio puesto."),
    (T["bCartel"], T["bNadie"], "2 · LA TIENDA", "Ni un cartel que diga qué venden."),
    (T["bNadie"], T["comprasAhi"], "2 · LA TIENDA", "Y el que te mira desde el fondo no sonríe."),
    (T["comprasAhi"], T["storeOut"], "2 · LA TIENDA", "¿Tú compras ahí?"),
    (T["web"], T["rGarantia"], "3 · REMATE", "Pues así entra el cliente a tu tienda online cuando no hay ni una reseña,"),
    (T["rGarantia"], T["masGente"], "3 · REMATE", "no se ve la garantía y no sabe si le va a llegar el pedido."),
    (T["masGente"], T["fix"], "3 · REMATE", "Y tú, metiendo más gente por la puerta."),
    (T["fix"], T["card1"], "4 · SOLUCIÓN", "Antes de traer más gente, arregla esto."),
    (T["card1"], T["card2"], "4 · SOLUCIÓN", "Que se vea qué vendes,"),
    (T["card2"], T["card3"], "4 · SOLUCIÓN", "que haya reseñas"),
    (T["card3"], T["confianza"] + 1.5, "4 · SOLUCIÓN", "y que quede claro qué pasa si algo sale mal."),
]
if proof:
    LINES.append((T["proof"], T["cta"], "5 · PRUEBA", "Es lo primero que miro en mis tiendas."))
LINES += [
    (T["cta"], T["send"], "6 · ACCIÓN", "Comenta TIENDA"),
    (T["send"], info["duration"], "6 · ACCIÓN", "y te mando la lista de lo que tiene que haber en cada parte de tu tienda."),
]


def ts(s):
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Scene,Inter Display SemiBold,34,&H0000FFFF,&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,3,10,0,9,40,40,70,1
Style: Voice,Inter Display SemiBold,42,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,3,14,0,2,70,70,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open("out/guide.ass", "w") as f:
    f.write(head)
    for a, b, scene, voice in LINES:
        f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Scene,,0,0,0,,{scene}\n")
        f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Voice,,0,0,0,,VOZ: {voice}\n")
print("out/guide.ass", len(LINES), "frases")
