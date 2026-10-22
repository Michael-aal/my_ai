"""
action_engine.py
────────────────
Unified executor: receives structured intent dict,
runs system actions, returns clean responses for TTS.
"""

import os
import sys
import shutil
import subprocess
import re
import datetime

try:
    import psutil
except ImportError:
    psutil = None

# ─────────────────────────────────────────
# PLATFORM
# ─────────────────────────────────────────

PLATFORM = sys.platform

NIRCMD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nircmd.exe")

def _plat():
    return PLATFORM if PLATFORM in ("darwin", "win32") else "linux"


# ─────────────────────────────────────────
# SAFE SPEAK (CRITICAL FIX)
# ─────────────────────────────────────────

def speak(text: str):
    if not text:
        return
    text = str(text)
    print(f"[Jarvis] {text}")

    plat = _plat()
    if plat == "darwin":
        subprocess.Popen(["say", "-r", "200", text])
    elif plat == "win32":
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$s.Speak({repr(text)})"
        )
        subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script])
    elif plat == "linux":
        engine = shutil.which("espeak") or shutil.which("spd-say")
        if engine:
            subprocess.Popen([engine, text])


# ─────────────────────────────────────────
# APP PATHS (WINDOWS SPECIFIC)
# ─────────────────────────────────────────

WIN_EXE_PATHS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "notepad": r"C:\Windows\System32\notepad.exe",
    "explorer": r"C:\Windows\explorer.exe",
    "calc": r"C:\Windows\System32\calc.exe",
    "cmd": r"C:\Windows\System32\cmd.exe",
    "taskmgr": r"C:\Windows\System32\Taskmgr.exe",
    "mspaint": r"C:\Windows\System32\mspaint.exe",
    "vscode": os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
}

WIN_PROC_NAMES = {
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "vlc": "vlc.exe",
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "taskmgr": "Taskmgr.exe",
    "mspaint": "mspaint.exe",
    "vscode": "Code.exe",
}


# ─────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────

def _safe_result(ok: bool, msg: str = ""):
    return {"ok": ok, "msg": msg}


# ─────────────────────────────────────────
# APP CONTROL
# ─────────────────────────────────────────

def _open_app(app: str):
    app = (app or "").lower().strip()

    if not app:
        return _safe_result(False, "No app provided")

    if _plat() == "win32":
        exe = WIN_EXE_PATHS.get(app)
        if not exe:
            return _safe_result(False, f"{app} not allowed")

        if not os.path.exists(exe):
            return _safe_result(False, f"{app} not installed")

        subprocess.Popen([exe], shell=False)
        return _safe_result(True, f"Opened {app}")

    return _safe_result(False, "Unsupported OS")


def _close_app(app: str):
    app = re.sub(r"[^a-z0-9]", "", (app or "").lower().strip())  # whitelist chars
    proc = WIN_PROC_NAMES.get(app)
    if not proc:
        return _safe_result(False, f"{app} not in allowed list")
    if _plat() == "win32":
        result = subprocess.run(["taskkill", "/F", "/IM", proc], capture_output=True)
        ok = result.returncode == 0
        return _safe_result(ok, f"{'Closed' if ok else 'Failed to close'} {app}")
    return _safe_result(False, "Unsupported OS")


def _open_url(url: str):
    if not url:
        return _safe_result(False, "No URL")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if _plat() == "win32":
        os.startfile(url)
    else:
        os.system(f'xdg-open "{url}" &')

    return _safe_result(True, f"Opened {url}")


def _screenshot():
    ts = int(datetime.datetime.now().timestamp())
    out = os.path.join(os.path.expanduser("~"), "Desktop", f"jarvis_{ts}.png")

    if _plat() == "win32":
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "Add-Type -AssemblyName System.Drawing;"
            "$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
            "$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height);"
            "$g=[System.Drawing.Graphics]::FromImage($b);"
            "$g.CopyFromScreen(0,0,0,0,$b.Size);"
            f'$b.Save("{out}");$g.Dispose();$b.Dispose()'
        )
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
        if r.returncode != 0:
            return _safe_result(False, "Screenshot failed")
    elif _plat() == "darwin":
        subprocess.run(["screencapture", "-x", out])
    else:
        return _safe_result(False, "Screenshot not supported on this OS")

    return _safe_result(True, f"Screenshot saved to {out}")


def _audio(action: str):
    if _plat() == "win32" and os.path.exists(NIRCMD):
        cmd = {
            "mute": ["mutesysvolume", "1"],
            "unmute": ["mutesysvolume", "0"],
            "volume_up": ["changesysvolume", "6553"],
            "volume_down": ["changesysvolume", "-6553"],
        }[action]
        subprocess.run([NIRCMD] + cmd, capture_output=True)
        return _safe_result(True, action.replace("_", " "))
    return _safe_result(False, "Audio control not available")


def _brightness(direction: str):
    if _plat() == "win32":
        delta = 10 if direction == "up" else -10
        ps = (
            "$b=(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness;"
            f"$n=[Math]::Max(0,[Math]::Min(100,$b+({delta})));"
            "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
            ".WmiSetBrightness(1,$n)"
        )
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
        ok = r.returncode == 0
        return _safe_result(ok, f"Brightness {direction}" if ok else "Brightness control failed")
    return _safe_result(False, "Brightness not supported on this OS")


def _wifi(state: str):
    if _plat() == "win32":
        action = "enable" if state == "on" else "disable"
        r = subprocess.run(
            ["netsh", "interface", "set", "interface", "Wi-Fi", action],
            capture_output=True,
        )
        ok = r.returncode == 0
        return _safe_result(ok, f"Wi-Fi {state}" if ok else f"Failed to turn Wi-Fi {state}")
    return _safe_result(False, "Wi-Fi control not supported on this OS")


def _empty_trash():
    if _plat() == "win32":
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
            capture_output=True,
        )
        return _safe_result(True, "Recycle bin emptied")
    return _safe_result(False, "Empty trash not supported on this OS")


def _query_battery():
    if not psutil:
        return "Battery info requires psutil"
    bat = psutil.sensors_battery()
    if bat is None:
        return "No battery detected"
    pct = int(bat.percent)
    state = "charging" if bat.power_plugged else "discharging"
    return f"Battery at {pct} percent, {state}"


def _query_ram():
    if not psutil:
        return "RAM info requires psutil"
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)
    return f"Using {used_gb:.1f} of {total_gb:.1f} gigabytes of RAM, {mem.percent} percent used"


def _send_whatsapp(name: str, message: str):
    if not name or not message:
        return _safe_result(False, "Need a contact and a message")
    try:
        from whatsapp_bot import send_message
        send_message(name, message)
        return _safe_result(True, f"Message sent to {name}")
    except Exception as e:
        return _safe_result(False, f"WhatsApp unavailable: {e}")


# ─────────────────────────────────────────
# ACTION EXECUTOR (MAIN FUNCTION)
# ─────────────────────────────────────────

def perform_action(intent: dict):
    """
    Safe executor — never crashes even with bad input
    """
    if not isinstance(intent, dict):
        return "Invalid intent"

    action = intent.get("intent", None)

    if not action:
        return "No action detected"

    # ── OPEN APP ───────────────────────────
    if action == "open_app":
        return _open_app(intent.get("app", "")).get("msg", "")

    # ── CLOSE APP ──────────────────────────
    if action == "close_app":
        return _close_app(intent.get("app", "")).get("msg", "")

    # ── URL ────────────────────────────────
    if action == "open_url":
        return _open_url(intent.get("url", "")).get("msg", "")

    # ── OPEN BROWSER ──────────────────────
    if action == "open_browser":
        app = intent.get("app") or "chrome"
        return _open_app(app).get("msg", "")

    # ── SCREENSHOT ─────────────────────────
    if action == "screenshot":
        return _screenshot().get("msg", "")

    # ── AUDIO ──────────────────────────────
    if action in ("mute", "unmute", "volume_up", "volume_down"):
        return _audio(action).get("msg", "")

    # ── BRIGHTNESS ─────────────────────────
    if action in ("brightness_up", "brightness_down"):
        return _brightness(action).get("msg", "")

    # ── WIFI ───────────────────────────────
    if action in ("wifi_on", "wifi_off"):
        return _wifi("on" if action == "wifi_on" else "off").get("msg", "")

    # ── EMPTY TRASH ────────────────────────
    if action == "empty_trash":
        return _empty_trash().get("msg", "")

    # ── INFO QUERIES ───────────────────────
    if action == "query_time":
        return "It is " + datetime.datetime.now().strftime("%I:%M %p")

    if action == "query_date":
        return "Today is " + datetime.datetime.now().strftime("%A, %B %d, %Y")

    if action == "query_battery":
        return _query_battery()

    if action == "query_ram":
        return _query_ram()

    # ── WHATSAPP ───────────────────────────
    if action == "send_whatsapp":
        return _send_whatsapp(intent.get("name", ""), intent.get("message", "")).get("msg", "")

    # ── SYSTEM ─────────────────────────────
    if action == "shutdown":
        if _plat() == "win32":
            os.system("shutdown /s /t 0")
        elif _plat() == "darwin":
            os.system("osascript -e 'tell app \"System Events\" to shut down'")
        else:
            os.system("sudo shutdown now")
        return "Shutting down"

    if action == "restart":
        if _plat() == "win32":
            os.system("shutdown /r /t 0")
        elif _plat() == "darwin":
            os.system("osascript -e 'tell app \"System Events\" to restart'")
        else:
            os.system("sudo reboot")
        return "Restarting"

    if action == "sleep":
        if _plat() == "win32":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif _plat() == "darwin":
            os.system("osascript -e 'tell app \"System Events\" to sleep'")
        else:
            os.system("systemctl suspend")
        return "Sleeping"

    if action == "lock":
        if _plat() == "win32":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif _plat() == "darwin":
            os.system("osascript -e 'tell app \"System Events\" to keystroke \"q\" using {command down, control down}'")
        else:
            os.system("gnome-screensaver-command -l")  # or another Linux lock command
        return "Locked"

    # ── MEMORY ─────────────────────────────
    if action == "memory_save":
        try:
            from database import set_info
            set_info(intent.get("key", ""), intent.get("value", ""))
            return f"Saved {intent.get('key', '')}"
        except Exception:
            return "Could not save to memory"

    if action == "memory_recall":
        try:
            from database import get_info
            value = get_info(intent.get("key", ""))
            return value if value else "No data found"
        except Exception:
            return "Could not read memory"

    if action == "memory_forget":
        try:
            from database import conn, c
            c.execute("DELETE FROM user_info WHERE key=?", (intent.get("key", "").strip().lower(),))
            conn.commit()
            return f"Forgot {intent.get('key', '')}"
        except Exception:
            return "Could not forget memory"

    if action == "memory_show":
        try:
            from database import get_all_info
            rows = get_all_info()
            if not rows:
                return "Memory is empty"
            return "; ".join(f"{k} is {v}" for k, v in rows)
        except Exception:
            return "Could not show memory"

    # ── AI FALLBACK ────────────────────────
    if action == "ask_claude":
        text = intent.get("text", "")

        if not text:
            return "Empty prompt"

        try:
            from ai_engine import get_ai_response
            response = get_ai_response(text)
            return response or "No response"
        except Exception:
            return "AI brain unavailable"

    # ── EXIT ───────────────────────────────
    if action == "exit":
        return "Goodbye"

    # ── UNKNOWN ────────────────────────────
    return f"Unknown action: {action}"


# Alias expected by README and tools.py
execute = perform_action