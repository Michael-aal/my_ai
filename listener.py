import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import noisereduce as nr
import time
import collections
import os
import sys
import shutil

# ─── Config ────────────────────────────────────────────────────────────────────
SAMPLERATE        = 16000
CHUNK_DURATION    = 0.03          # 30ms frames (VAD standard)
CHUNK_SIZE        = int(SAMPLERATE * CHUNK_DURATION)
SILENCE_THRESHOLD = 0.012         # RMS energy threshold
SPEECH_PAD_MS     = 300           # ms of silence before cutting off
SPEECH_PAD_CHUNKS = int(SPEECH_PAD_MS / (CHUNK_DURATION * 1000))
MIN_SPEECH_CHUNKS = 8             # ignore clips shorter than ~240ms (noise bursts)
MAX_RECORD_SEC    = 12            # hard cap per utterance
WAKE_WORD_MODE    = True          # False = act on every word, no wake word needed
WAKE_WORDS        = ["javis","code", "hey michael", "michael", "hello michael"]

print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper ready\n")

# ─── Energy-based VAD ─────────────────────────────────────────────────────────

def rms(chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(chunk ** 2)))

def is_speech(chunk: np.ndarray) -> bool:
    return rms(chunk) > SILENCE_THRESHOLD

# ─── Noise reduction + normalization ──────────────────────────────────────────

def preprocess(audio: np.ndarray) -> np.ndarray:
    if np.max(np.abs(audio)) < 0.005:
        return audio
    try:
        audio = nr.reduce_noise(y=audio, sr=SAMPLERATE, prop_decrease=0.85)
    except Exception:
        pass
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.95
    return audio

# ─── Transcribe ───────────────────────────────────────────────────────────────

HALLUCINATIONS = {
    "thank you", "thanks for watching", "you", "bye", "thanks",
    ".", "..", "...", "the", "", "goodbye", "see you next time",
}

def transcribe(audio: np.ndarray) -> str:
    audio = preprocess(audio)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav.write(tmp.name, SAMPLERATE, (audio * 32767).astype(np.int16))
        path = tmp.name
    try:
        result = model.transcribe(
            path,
            fp16=False,
            language="en",
            temperature=0,
            no_speech_threshold=0.5,
            logprob_threshold=-0.8,
            compression_ratio_threshold=2.4,
            condition_on_previous_text=False,
        )
        text = result["text"].strip().lower()
        if text in HALLUCINATIONS or len(text) < 2:
            return ""
        return text
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

# ─── Smart VAD Recorder ───────────────────────────────────────────────────────

def record_utterance() -> np.ndarray | None:
    """
    Streams 30ms chunks. Captures user speech until silence, then waits 5 seconds after the last speech chunk before processing.
    """
    speech_chunks = []
    pre_buffer = collections.deque(maxlen=15)

    in_speech = False
    last_speech_time = None
    started = False

    stream = sd.InputStream(
        samplerate=SAMPLERATE,
        channels=1,
        dtype="float32",
        blocksize=CHUNK_SIZE,
    )

    with stream:
        while True:
            chunk, _ = stream.read(CHUNK_SIZE)
            chunk = chunk.flatten()

            speech = is_speech(chunk)
            now = time.time()

            if speech:
                last_speech_time = now

                if not in_speech:
                    # attach pre-roll audio
                    speech_chunks.extend(list(pre_buffer))
                    in_speech = True

                speech_chunks.append(chunk)
                started = True  # we started speaking

            else:
                if in_speech:
                    speech_chunks.append(chunk)
                    # Check how long it’s been since last speech
                    if last_speech_time and (now - last_speech_time) >= 3.0:  # 3-second silence timeout
                        break

            if len(speech_chunks) > int(MAX_RECORD_SEC / CHUNK_DURATION):
                break  # safety cap

    if len(speech_chunks) < MIN_SPEECH_CHUNKS:
        return None

    return np.concatenate(speech_chunks)

# ─── Wake word helpers ────────────────────────────────────────────────────────

def contains_wake_word(text: str) -> bool:
    return any(w in text for w in WAKE_WORDS)

def strip_wake_word(text: str) -> str:
    for w in sorted(WAKE_WORDS, key=len, reverse=True):
        text = text.replace(w, "").strip(" ,.")
    return text.strip()

# ─── OS helpers — pure os.system, zero subprocess ─────────────────────────────

def _open_app(linux_cmd: str, mac_app: str, win_cmd: str):
    if sys.platform == "darwin":
        os.system(f'open -a "{mac_app}" &')
    elif sys.platform == "win32":
        os.system(f'start "" "{win_cmd}"')
    else:
        os.system(f"nohup {linux_cmd} >/dev/null 2>&1 &")

def _screenshot():
    ts   = int(time.time())
    home = os.path.expanduser("~")
    out  = os.path.join(home, "Desktop", f"aria_{ts}.png")

    if sys.platform == "darwin":
        os.system(f'screencapture -x "{out}"')

    elif sys.platform == "win32":
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "Add-Type -AssemblyName System.Drawing;"
            "$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
            "$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height);"
            "$g=[System.Drawing.Graphics]::FromImage($b);"
            "$g.CopyFromScreen(0,0,0,0,$b.Size);"
            f'$b.Save("{out}");$g.Dispose();$b.Dispose()'
        )
        os.system(f'powershell -NoProfile -Command "{ps}"')

    else:
        if shutil.which("scrot"):
            os.system(f'scrot "{out}"')
        elif shutil.which("gnome-screenshot"):
            os.system(f'gnome-screenshot -f "{out}"')
        elif shutil.which("import"):
            os.system(f'import -window root "{out}"')
        else:
            print("  No screenshot tool found — install scrot")
            return

    print(f"  Saved: {out}")

def _mute():
    if sys.platform == "darwin":
        os.system("osascript -e 'set volume output muted true'")
    elif sys.platform == "win32":
        os.system('powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]173)"')
    else:
        os.system("pactl set-sink-mute @DEFAULT_SINK@ 1")

def _unmute():
    if sys.platform == "darwin":
        os.system("osascript -e 'set volume output muted false'")
    elif sys.platform == "win32":
        os.system('powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]173)"')
    else:
        os.system("pactl set-sink-mute @DEFAULT_SINK@ 0")

def _volume(delta: str):
    if sys.platform == "darwin":
        op = "+" if "+" in delta else "-"
        os.system(
            f"osascript -e 'set volume output volume "
            f"((output volume of (get volume settings)) {op} 10)'"
        )
    elif sys.platform == "win32":
        key = 175 if "+" in delta else 174
        os.system(
            f'powershell -c "1..5 | % '
            f'{{(New-Object -comObject WScript.Shell).SendKeys([char]{key})}}"'
        )
    else:
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {delta}")

def _brightness(direction: str):
    if sys.platform == "darwin":
        key = 144 if direction == "up" else 145
        os.system(f"osascript -e 'tell application \"System Events\" to key code {key}'")
    elif sys.platform == "win32":
        delta = 10 if direction == "up" else -10
        ps = (
            "$b=(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness)"
            ".CurrentBrightness;"
            f"$n=[Math]::Max(0,[Math]::Min(100,$b+({delta})));"
            "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
            ".WmiSetBrightness(1,$n)"
        )
        os.system(f'powershell -NoProfile -Command "{ps}"')
    else:
        val    = 1.2 if direction == "up" else 0.8
        screen = os.popen(
            "xrandr | grep ' connected' | head -1 | cut -d' ' -f1"
        ).read().strip()
        if screen:
            os.system(f"xrandr --output {screen} --brightness {val}")

def _lock():
    if sys.platform == "darwin":
        os.system(
            "osascript -e 'tell application \"System Events\" "
            "to keystroke \"q\" using {command down, control down}'"
        )
    elif sys.platform == "win32":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    else:
        os.system("loginctl lock-session")

def _shutdown():
    if sys.platform == "darwin":
        os.system("osascript -e 'tell app \"System Events\" to shut down'")
    elif sys.platform == "win32":
        os.system("shutdown /s /t 0")
    else:
        os.system("sudo shutdown -h now")

def _wifi(state: str):
    if sys.platform == "darwin":
        os.system(f"networksetup -setairportpower airport {state}")
    elif sys.platform == "win32":
        action = "enable" if state == "on" else "disable"
        os.system(f'netsh interface set interface "Wi-Fi" {action}')
    else:
        os.system(f"nmcli radio wifi {state}")

def _empty_trash():
    if sys.platform == "darwin":
        os.system("osascript -e 'tell app \"Finder\" to empty trash'")
    elif sys.platform == "win32":
        os.system('powershell -c "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"')
    else:
        os.system("rm -rf ~/.local/share/Trash/files/* ~/.local/share/Trash/info/*")

# ─── Claude API fallback ──────────────────────────────────────────────────────

def _ask_claude(text: str):
    try:
        import anthropic
        client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from env
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=(
                "You are ARIA, a concise laptop voice assistant. "
                "Answer in 1-2 sentences max."
            ),
            messages=[{"role": "user", "content": text}],
        )
        reply = msg.content[0].text
        print(f"[ARIA] {reply}")
    except ImportError:
        print(f'[ARIA] Unknown: "{text}" — pip install anthropic for AI fallback')
    except Exception as e:
        print(f"[ARIA] Claude error: {e}")

# ─── Command dispatcher ───────────────────────────────────────────────────────

def handle_command(text: str):
    text = strip_wake_word(text)
    if not text:
        return

    print(f'\n[ARIA] Heard: "{text}"')

    t = text  # alias

    if any(x in t for x in ["open chrome", "launch chrome"]):
        print("  Opening Chrome")
        _open_app("google-chrome", "Google Chrome", "chrome")

    elif any(x in t for x in ["open terminal", "launch terminal"]):
        print("  Opening Terminal")
        _open_app("x-terminal-emulator", "Terminal", "cmd")

    elif any(x in t for x in ["open notepad", "open notes", "open text"]):
        print("  Opening text editor")
        _open_app("gedit", "TextEdit", "notepad")

    elif any(x in t for x in ["open spotify", "play music"]):
        print("  Opening Spotify")
        _open_app("spotify", "Spotify", "spotify")

    elif any(x in t for x in ["open vs code", "open vscode", "open code"]):
        print("  Opening VS Code")
        _open_app("code", "Visual Studio Code", "Code")

    elif any(x in t for x in ["open finder", "open files", "file manager"]):
        print("  Opening files")
        _open_app("xdg-open ~", "Finder", "explorer .")

    elif any(x in t for x in ["take screenshot", "screenshot", "capture screen"]):
        print("  Taking screenshot")
        _screenshot()

    elif any(x in t for x in ["unmute", "sound on", "audio on"]):
        print("  Unmuting")
        _unmute()

    elif any(x in t for x in ["mute", "silence"]):
        print("  Muting")
        _mute()

    elif any(x in t for x in ["volume up", "louder", "turn up"]):
        print("  Volume up")
        _volume("+10%")

    elif any(x in t for x in ["volume down", "quieter", "turn down"]):
        print("  Volume down")
        _volume("-10%")

    elif any(x in t for x in ["brightness up", "brighter"]):
        print("  Brightness up")
        _brightness("up")

    elif any(x in t for x in ["brightness down", "dimmer"]):
        print("  Brightness down")
        _brightness("down")

    elif any(x in t for x in ["what time", "current time", "tell me the time"]):
        print(f"  Time: {time.strftime('%I:%M %p')}")

    elif any(x in t for x in ["what date", "today's date", "what day"]):
        print(f"  Date: {time.strftime('%A, %B %d %Y')}")

    elif any(x in t for x in ["lock screen", "lock computer", "lock"]):
        print("  Locking screen")
        _lock()

    elif any(x in t for x in ["wifi on", "enable wifi", "turn on wifi"]):
        print("  Wi-Fi on")
        _wifi("on")

    elif any(x in t for x in ["wifi off", "disable wifi", "turn off wifi"]):
        print("  Wi-Fi off")
        _wifi("off")

    elif any(x in t for x in ["empty trash", "clear trash"]):
        print("  Emptying trash")
        _empty_trash()

    elif any(x in t for x in ["shutdown", "shut down", "power off"]):
        print("  Shutting down")
        _shutdown()

    elif any(x in t for x in ["stop", "quit", "exit", "goodbye", "bye aria"]):
        print("  Goodbye!")
        sys.exit(0)

    else:
        _ask_claude(text)

# ─── Main loop ────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  ARIA Voice Engine  —  Whisper + Smart VAD")
    print("=" * 50)
    print(f"  Wake words : {', '.join(WAKE_WORDS)}")
    print(f"  Wake mode  : {'ON' if WAKE_WORD_MODE else 'OFF (all speech acted on)'}")
    print(f"  Silence pad: {SPEECH_PAD_MS}ms")
    print(f"  Max record : {MAX_RECORD_SEC}s")
    print(f"  Python     : {sys.version.split()[0]}")
    print("=" * 50)
    print("\nListening...\n")

    while True:
        try:
            audio = record_utterance()

            if audio is None:
                continue

            if rms(audio) < SILENCE_THRESHOLD * 0.05:
                continue

            print("[transcribing...]", end="\r")
            text = transcribe(audio)

            if not text:
                continue

            if WAKE_WORD_MODE:
                if contains_wake_word(text):
                    handle_command(text)
                else:
                    print(f'[standby] "{text}"')
            else:
                handle_command(text)

        except KeyboardInterrupt:
            print("\n\nARIA stopped. Goodbye!")
            break
        except Exception as e:
            print(f"[error] {e}")
            time.sleep(0.3)

if __name__ == "__main__":
    main()