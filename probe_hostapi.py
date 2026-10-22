import sounddevice as sd
import numpy as np
import threading

print("=== host APIs ===")
for i, h in enumerate(sd.query_hostapis()):
    print(f"{i}: {h['name']} (default_in={h['default_input_device']})")

wasapi = next((i for i, h in enumerate(sd.query_hostapis()) if "WASAPI" in h["name"]), None)
print("\n=== WASAPI input devices ===")
if wasapi is not None:
    devs = sd.query_hostapis(wasapi)["devices"]
    for gi in devs:
        d = sd.query_devices(gi)
        if d["max_input_channels"] > 0:
            mark = " <<< BT" if ("Headset" in d["name"] or "Hands-Free" in d["name"] or "TWS" in d["name"] or "MG-S20" in d["name"] or "F109" in d["name"]) else ""
            print(f"  {gi}: {d['name'][:70]} sr={int(d['default_samplerate'])}{mark}")

print("\n=== callback-mode test on WDM-KS device 24 (TWS PRO) ===")
done = threading.Event()
level = {"v": None}

def cb(indata, frames, time_info, status):
    level["v"] = float(np.sqrt(np.mean(indata ** 2)))
    done.set()

try:
    with sd.InputStream(samplerate=8000, channels=1, dtype="float32",
                        device=24, callback=cb, blocksize=int(8000 * 0.4)):
        done.wait(timeout=5)
    print(f"callback OK, level={level['v']:.5f}" if level["v"] is not None else "callback: no data")
except Exception as e:
    print(f"callback FAILED: {type(e).__name__}: {e}")
