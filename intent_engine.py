"""
Layer 1 — The ears.
Converts raw text into structured intent dict.
"""

import re

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def _is_url(token: str) -> bool:
    if not token:
        return False

    pattern = re.compile(
        r"^(https?://)?"
        r"([\w\-]+\.)+[a-z]{2,}"
        r"(/[\w\-._~:/?#\[\]@!$&'()*+,;=%]*)?$",
        re.IGNORECASE,
    )
    return bool(pattern.match(token.strip()))

def _normalize_app_name(raw: str) -> str:
    if not raw:
        return ""

    raw = raw.lower().strip()

    aliases = {
        "google chrome": "chrome",
        "chrome": "chrome",
        "microsoft edge": "edge",
        "edge": "edge",
        "firefox": "firefox",
        "vlc": "vlc",
        "vlc media player": "vlc",
        "visual studio code": "vscode",
        "vs code": "vscode",
        "vscode": "vscode",
        "notepad": "notepad",
        "file explorer": "explorer",
        "explorer": "explorer",
        "calculator": "calc",
        "task manager": "taskmgr",
        "cmd": "cmd",
        "command prompt": "cmd",
        "paint": "mspaint",
        "spotify": "spotify",
        "whatsapp": "whatsapp",
    }

    return aliases.get(raw, raw)

def _clean(text: str) -> str:
    return text.strip().lower()

# ─────────────────────────────────────────
# STRICT SYSTEM INTENT MATCHES (MULTI-PHRASE)
# (prevents random misclassification like RAM bug)
# ─────────────────────────────────────────

SYSTEM_MAP = {
    "query_ram": [
        "ram",
        "check ram",
        "check ram usage",
        "memory usage",
        "how much memory",
        "what is the ram"
    ],
    "query_time": [
        "time",
        "what time is it",
        "current time",
        "tell me the time"
    ],
    "query_date": [
        "date",
        "what is the date",
        "today date",
        "what day is it"
    ],
    "shutdown": [
        "shutdown",
        "turn off pc",
        "off the laptop",
        "power off",
        "shut down",
        "switch off computer",
        "exit computer"
    ],
    "restart": [
        "restart",
        "reboot pc",
        "reboot computer",
        "restart laptop",
        "turn on again"
    ],
    "sleep": [
        "sleep",
        "go to sleep",
        "hibernate",
        "put the computer to sleep"
    ],
    "lock": [
        "lock",
        "lock screen",
        "secure the computer",
        "close screen"
    ],
    "mute": [
        "mute",
        "turn off sound",
        "silence audio",
        "no sound"
    ],
    "unmute": [
        "unmute",
        "turn on sound",
        "sound on",
        "restore audio"
    ],
    "volume_up": [
        "volume up",
        "increase volume",
        "louder",
        "turn up volume",
        "raise volume"
    ],
    "volume_down": [
        "volume down",
        "decrease volume",
        "quieter",
        "turn down volume",
        "lower volume"
    ],
    "screenshot": [
        "screenshot",
        "take screenshot",
        "capture screen",
        "print screen"
    ],
    "exit": [
        "exit",
        "stop jarvis",
        "quit jarvis",
        "close assistant",
        "end session"
    ],
}

def _match_strict(text: str) -> dict:
    for intent, phrases in SYSTEM_MAP.items():
        if text in phrases:
            return {"intent": intent}
    return None

# ─────────────────────────────────────────
# MAIN PARSER
# ─────────────────────────────────────────

def detect_intent(text: str) -> dict:
    if not text or not isinstance(text, str):
        return {"intent": "ask_claude", "text": ""}

    original = text.strip()
    text = _clean(text)

    # ─────────────────────────────────────────
    # 0. STRICT SYSTEM MATCH (FIXES YOUR BUG)
    # ─────────────────────────────────────────
    strict = _match_strict(text)
    if strict:
        return strict

    # ─────────────────────────────────────────
    # 1. MEMORY
    # ─────────────────────────────────────────

    m = re.match(r"remember (.+?) is (.+)", text)
    if m:
        return {
            "intent": "memory_save",
            "key": m.group(1).strip(),
            "value": m.group(2).strip()
        }

    if text.startswith("what is "):
        return {
            "intent": "memory_recall",
            "key": text.replace("what is ", "").strip()
        }

    if text == "show memory":
        return {"intent": "memory_show"}

    # ─────────────────────────────────────────
    # 2. WHATSAPP
    # ─────────────────────────────────────────

    wa_patterns = [
        r"send (?:a )?(?:whatsapp )?message to (\w+)\s+(.+)",
        r"whatsapp (\w+) (?:saying|say)\s+(.+)",
        r"message (\w+) (?:on whatsapp\s+)?(.+)",
    ]

    for pat in wa_patterns:
        m = re.match(pat, text)
        if m:
            return {
                "intent": "send_whatsapp",
                "name": m.group(1).strip(),
                "message": m.group(2).strip(),
            }

    # ─────────────────────────────────────────
    # 3. URL OPEN
    # ─────────────────────────────────────────

    url_prefixes = ("open ", "go to ", "visit ", "browse ", "navigate to ")

    for prefix in url_prefixes:
        if text.startswith(prefix):
            candidate = text[len(prefix):].strip()

            if _is_url(candidate):
                url = candidate if candidate.startswith("http") else "https://" + candidate
                return {"intent": "open_url", "url": url}

    if _is_url(text):
        url = text if text.startswith("http") else "https://" + text
        return {"intent": "open_url", "url": url}

    # ─────────────────────────────────────────
    # 4. APP CONTROL
    # ─────────────────────────────────────────

    for prefix in ("open ", "launch ", "start ", "run "):
        if text.startswith(prefix):
            app = text[len(prefix):].strip()
            return {
                "intent": "open_app",
                "app": _normalize_app_name(app),
            }

    for prefix in ("close ", "kill ", "quit ", "exit ", "stop "):
        if text.startswith(prefix):
            app = text[len(prefix):].strip()
            return {
                "intent": "close_app",
                "app": _normalize_app_name(app),
            }

    # ─────────────────────────────────────────
    # 5. SEARCH
    # ─────────────────────────────────────────

    for prefix in ("search ", "google ", "look up ", "find "):
        if text.startswith(prefix):
            query = text[len(prefix):].strip()
            return {
                "intent": "open_url",
                "url": f"https://www.google.com/search?q={query.replace(' ', '+')}"
            }

    # ─────────────────────────────────────────
    # 6. EXIT
    # ─────────────────────────────────────────

    if text in ("exit", "stop jarvis", "quit jarvis"):
        return {"intent": "exit"}

    # ─────────────────────────────────────────
    # 7. FALLBACK AI
    # ─────────────────────────────────────────

    return {
        "intent": "ask_claude",
        "text": original
    }