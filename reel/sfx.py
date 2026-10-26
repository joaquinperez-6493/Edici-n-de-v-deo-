"""Sintetiza la pista de efectos (sin música) a partir de out/cues.json.

Efectos: swoosh, pop, thud (golpe seco), ding (check), tick, blip, key (tecla).
Salida: out/sfx.wav (48 kHz, estéreo, volumen bajo).
"""
import json
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def env(n, attack, decay):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / decay)


def lowpass(x, cutoff):
    # filtro de un polo, suficiente para suavizar ruido
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def swoosh():
    n = int(.42 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    # barrido de brillo: mezcla de ruido filtrado grave y agudo con envolvente en campana
    lo, hi = lowpass(noise, 900), noise - lowpass(noise, 2500)
    k = t / t[-1]
    x = lo * (1 - k) + hi * k * .6
    bell = np.sin(np.pi * k) ** 2
    return x * bell * .5


def pop():
    n = int(.12 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 30) + 380
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .035) * .7


def thud():
    n = int(.5 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 18) + 48
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .003, .16)
    click = lowpass(rng.standard_normal(n), 3000) * env(n, .0005, .012) * .8
    return (body + click) * .9


def ding():
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 1318.5 * t) * .6 + np.sin(2 * np.pi * 1975.5 * t) * .3
         + np.sin(2 * np.pi * 2637 * t) * .12)
    return x * env(n, .003, .28) * .45


def tick():
    n = int(.03 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * env(n, .0005, .006) * .5


def blip():
    n = int(.08 * SR)
    t = np.arange(n) / SR
    f = 500 - 250 * t / t[-1]
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .03) * .5


def key():
    n = int(.04 * SR)
    noise = rng.standard_normal(n) - lowpass(rng.standard_normal(n), 1500)
    return noise * env(n, .0005, .008) * .2


SYNTH = {"swoosh": swoosh, "pop": pop, "thud": thud, "ding": ding, "tick": tick, "blip": blip, "key": key}


def main():
    info = json.load(open("out/cues.json"))
    dur = info["duration"]
    mix = np.zeros((int(dur * SR) + SR, 2))
    for i, c in enumerate(info["cues"]):
        s = SYNTH[c["type"]]() * c["gain"]
        a = int(c["t"] * SR)
        pan = .5 + .12 * np.sin(i * 1.7)  # ligera variación estéreo
        seg = mix[a:a + len(s)]
        seg[:, 0] += s[:len(seg)] * (1 - pan) * 2 ** .5
        seg[:, 1] += s[:len(seg)] * pan * 2 ** .5
    mix = mix[: int(dur * SR)]
    peak = np.abs(mix).max()
    mix *= 10 ** (-12 / 20) / peak  # pico a -12 dBFS: volumen bajo
    pcm = (mix * 32767).astype(np.int16)
    with wave.open("out/sfx.wav", "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"out/sfx.wav · {len(info['cues'])} efectos · {dur:.1f} s")


if __name__ == "__main__":
    main()
