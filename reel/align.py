"""Transcribe la voz con marcas de tiempo por palabra -> out/words.json"""
import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(sys.argv[1], language="es", word_timestamps=True)
words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
json.dump(words, open("out/words.json", "w"), ensure_ascii=False, indent=0)
print(" ".join(f"{x['w']}@{x['s']}" for x in words))
