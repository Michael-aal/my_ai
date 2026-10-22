import sounddevice as sd
import traceback

# Try each headset mic at ITS OWN native sample rate
targets = [24, 26, 28, 30]
for idx in targets:
    d = sd.query_devices(idx)
    native = int(d["default_samplerate"])
    print(f"\n[{idx}] {d['name'][:70]} native={native}Hz")
    for sr in (native, 16000, 8000, 44100, 48000):
        try:
            with sd.InputStream(samplerate=sr, channels=1, dtype="float32",
                                device=idx, blocksize=int(sr * 0.3)) as s:
                data, _ = s.read(int(sr * 0.4))
            import numpy as np
            lvl = float(np.sqrt(np.mean(np.asarray(data) ** 2)))
            print(f"    sr={sr}: OK, level={lvl:.5f}")
            break
        except Exception as e:
            print(f"    sr={sr}: {type(e).__name__}: {str(e)[:120]}")
