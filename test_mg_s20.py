"""Find the MG-S20 Hands-Free mic by name (indices shift) and record 5s."""
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav

SR = 16000

def find_mg_s20():
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and "MG-S20" in d["name"] and "Hands-Free" not in d["name"]:
            # both "Headset (MG-S20)" MME and WDM-KS match; prefer MME/hostapi 0
            if d["hostapi"] == 0:
                return i, d
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and "MG-S20" in d["name"]:
            return i, d
    return None, None

idx, dev = find_mg_s20()
if idx is None:
    raise SystemExit("MG-S20 mic not found")

print(f"Using device {idx}: {dev['name'][:60]} sr={int(dev['default_samplerate'])}")
print("RECORDING 5s — SAY SOMETHING NOW")

native = int(dev["default_samplerate"])
with sd.InputStream(samplerate=native, channels=1, dtype="float32",
                    device=idx, blocksize=native) as s:
    frames = []
    for i in range(5):
        data, _ = s.read(native)
        a = np.asarray(data).flatten()
        frames.append(a)
        print(f"  sec {i+1}: rms={np.sqrt(np.mean(a**2)):.5f} peak={np.max(np.abs(a)):.5f}")

audio = np.concatenate(frames)

# resample native -> 16k for whisper
if native != SR:
    n = int(len(audio) * SR / native)
    audio = np.interp(np.linspace(0, len(audio) - 1, n),
                      np.arange(len(audio)), audio).astype(np.float32)

wav.write("mg_s20_test.wav", SR, (audio * 32767).astype(np.int16))
print(f"\noverall rms={np.sqrt(np.mean(audio**2)):.5f} — transcribing...")

import whisper
m = whisper.load_model("base")
r = m.transcribe(audio.astype(np.float32), fp16=False, language="en")
print("TRANSCRIPT:", repr(r["text"]))
