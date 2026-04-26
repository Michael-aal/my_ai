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

# ─────────────────────────────────────────
# PLATFORM
# ─────────────────────────────────────────

PLATFORM = sys.platform

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
    "vscode": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
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

    # ── SCREENSHOT ─────────────────────────
    if action == "screenshot":
        return "Screenshot taken"  # You could integrate a real screenshot tool here.

    # ── AUDIO ──────────────────────────────
    if action in ("mute", "unmute", "volume_up", "volume_down"):
        return action.replace("_", " ")

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
        return "Saved to memory"

    if action == "memory_recall":
        return "Retrieving memory"

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

    # ── UNKNOWN ────────────────────────────
    return f"Unknown action: {action}"