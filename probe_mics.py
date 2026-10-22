"""Probe every input device for 0.4s and print signal level.
Speak or tap the mic while this runs to see levels jump."""
import numpy as np
import sounddevice as sd

EXCLUDE = ("stereo mix", "midi")

def probe(idx, sr):
    try:
        with sd.InputStream(samplerate=sr, channels=1, dtype="float32",
                            device=idx, blocksize=int(sr * 0.4)) as s:
            data, _ = s.read(int(sr * 0.5))
        arr = np.asarray(data, dtype=np.float32).flatten()
        return float(np.sqrt(np.mean(arr ** 2)))
    except Exception as e:
        return f"FAIL: {type(e).__name__}"

print("Probing input devices (0.4s each)...\n")
for i, d in enumerate(sd.query_devices()):
    if d["max_input_channels"] == 0:
        continue
    name = d["name"]
    if any(x in name.lower() for x in EXCLUDE):
        print(f"{i}: {name} -> skipped (echo/aux)")
        continue
    native = int(d["default_samplerate"])
    # try 16k first, then native
    lvl = probe(i, 16000)
    used = 16000
    if isinstance(lvl, str):
        lvl = probe(i, native)
        used = native
    if isinstance(lvl, str):
        print(f"{i}: {name} -> {lvl}")
    else:
        live = "LIVE" if lvl >= 5e-5 else "silent"
        print(f"{i}: {name} @ {used}Hz -> level {lvl:.5f} [{live}]")
