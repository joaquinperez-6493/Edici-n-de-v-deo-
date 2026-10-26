"""Música de fondo original, sintetizada (sin derechos de terceros) -> out/music.wav

Base minimal a 96 BPM en La menor (Am-F-C-G). La estructura sigue las escenas
(lee los tiempos de out/cues.json): intro con tensión, ritmo completo en la tienda,
corte en seco en "¿Tú compras ahí?", y arpegio más brillante en la solución.
"""
import json
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 48000
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4
rng = np.random.default_rng(3)

info = json.load(open("out/cues.json"))
T, DUR = info["times"], info["duration"]
N = int(DUR * SR)
mix = np.zeros(N)


def lp(x, f):
    b, a = butter(2, f / (SR / 2))
    return lfilter(b, a, x)


def hp(x, f):
    b, a = butter(2, f / (SR / 2), "high")
    return lfilter(b, a, x)


def add(buf, t, gain=1.0):
    a = int(t * SR)
    if a >= N:
        return
    seg = buf[: N - a]
    mix[a:a + len(seg)] += seg * gain


def note_freq(m):
    return 440 * 2 ** ((m - 69) / 12)


def adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[n - nr:] *= np.linspace(1, 0, nr)
    return e


# acordes (MIDI): Am, F, C, G
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
ROOTS = [45, 41, 36, 43]


def pad(chord, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in chord:
        for det in (-0.08, 0.08):
            f = note_freq(m + det)
            x += 2 * (t * f % 1) - 1  # diente de sierra
    return lp(x, 900) * adsr(n, .6, .8) * .05


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = note_freq(m)
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(4 * np.pi * f * t)) * adsr(n, .01, .08) * .22


def kick():
    n = int(.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * .5


def clap():
    n = int(.2 * SR)
    t = np.arange(n) / SR
    return hp(lp(rng.standard_normal(n), 4000), 900) * np.exp(-t * 25) * .14


def hat():
    n = int(.06 * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * 70) * .07


def pluck(m):
    n = int(.5 * SR)
    t = np.arange(n) / SR
    f = note_freq(m)
    x = np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)
    return x * np.exp(-t * 7) * .06


K, C, H = kick(), clap(), hat()
drop_a, drop_b = T["comprasAhi"] - .15, T["web"]          # corte: solo queda el pad
bright = T["fix"]                                       # solución: arpegio
beat_in = T["storeIn"]

bar_i = 0
t = 0.0
while t < DUR:
    ch = bar_i % 4
    add(pad(CHORDS[ch], BAR + .6), t)
    for b in range(4):
        tb = t + b * BEAT
        in_drop = drop_a <= tb < drop_b
        # hats en corcheas desde el principio (tensión), suaves
        for h in (0, .5):
            if not in_drop:
                add(H, tb + h * BEAT, .6 if h == 0 else 1)
        if tb >= beat_in and not in_drop:
            if b in (0, 2):
                add(K, tb)
            if b in (1, 3):
                add(C, tb)
            add(bass(ROOTS[ch], BEAT * .9), tb)
        if tb >= bright and not in_drop:
            for k, off in enumerate((0, .5)):
                m = CHORDS[ch][(b * 2 + k) % 3] + 12
                add(pluck(m), tb + off * BEAT)
    t += BAR
    bar_i += 1

# golpe de entrada tras el corte
add(K, drop_b, 1.2)

# fundidos de entrada y salida
fade_in, fade_out = int(.4 * SR), int(1.2 * SR)
mix[:fade_in] *= np.linspace(0, 1, fade_in)
mix[-fade_out:] *= np.linspace(1, 0, fade_out)
mix /= np.abs(mix).max()
mix *= 10 ** (-6 / 20)

stereo = np.stack([mix, mix], 1)
with wave.open("out/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())
print(f"out/music.wav · {DUR:.1f} s · {BPM} BPM")
