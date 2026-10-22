"""Try EVERY MG-S20 input entry across all host APIs, rates, modes."""
import numpy as np
import sounddevice as sd

SR = 16000

cands = [(i, d) for i, d in enumerate(sd.query_devices())
         if d["max_input_channels"] > 0 and "MG-S20" in d["name"]]

if not cands:
    raise SystemExit("no MG-S20 input entries at all")

def probe_blocking(idx, sr):
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32",
                        device=idx, blocksize=max(1, int(sr * 0.3))) as s:
        data, _ = s.read(int(sr * 0.4))
    return float(np.sqrt(np.mean(np.asarray(data) ** 2)))

def probe_callback(idx, sr, secs=0.6):
    import threading
    done, lvl = threading.Event(), {}
    def cb(indata, frames, t, status):
        lvl["v"] = float(np.sqrt(np.mean(indata ** 2)))
        done.set()
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32",
                        device=idx, callback=cb, blocksize=int(sr * 0.3)):
        done.wait(timeout=secs)
    return lvl.get("v")

for idx, d in cands:
    api = sd.query_hostapis(d["hostapi"])["name"]
    native = int(d["default_samplerate"])
    print(f"\n[{idx}] {d['name'][:55]} | {api} | native={native}")
    for sr in dict.fromkeys((SR, native, 16000, 8000, 44100, 48000)):
        for fn_name, fn in (("blocking", probe_blocking), ("callback", probe_callback)):
            try:
                lvl = fn(idx, sr)
                print(f"    {fn_name} @ {sr}: OK level={lvl:.5f}")
                if lvl is not None and lvl >= 5e-5:
                    print(f"    ^^^ WORKING: device={idx} sr={sr} mode={fn_name}")
            except Exception as e:
                msg = str(e).split("'")[-2] if "'" in str(e) else str(e)
                print(f"    {fn_name} @ {sr}: FAIL {msg[:70]}")
