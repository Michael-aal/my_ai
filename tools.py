"""
tools.py
────────
All callable tools keyed by action string.
Used by action_engine.execute() via intent dispatch.
"""

import os
import webbrowser


def open_app(name):
    try:
        if name.startswith("http"):
            webbrowser.open(name)
            return f"Opening web: {name}"

        os.startfile(name)
        return f"Opening {name}"
    except Exception as e:
        return str(e)


def close_app(name):
    os.system(f"taskkill /f /im {name}.exe")
    return f"Closed {name}"


# Optional integrations — skip cleanly if dependency missing
try:
    from whatsapp_bot import open_whatsapp, send_message
except ImportError:
    open_whatsapp = None
    send_message = None

from file_controller import create_file, delete_file
from web_controller import search_web_tool

try:
    from system_control import (
        volume_up, volume_down, mute_volume, unmute,
        shutdown_pc, sleep_pc, restart_pc, lock_pc,
    )
except ImportError:
    volume_up = volume_down = mute_volume = unmute = None
    shutdown_pc = sleep_pc = restart_pc = lock_pc = None

from action_engine import (
    _open_app,
    _close_app,
    _open_url,
    execute,
)


def _optional(fn):
    """Wrap a possibly-None tool so calls fail with a clear message."""
    if fn is None:
        def _missing(**_):
            return "Tool unavailable (missing dependency)"
        return _missing
    return fn


# Re-export so callers can do: from tools import TOOLS
TOOLS = {
    "open_whatsapp": _optional(open_whatsapp),
    "send_message": _optional(send_message),

    "open_app": lambda app, **_: _open_app(app),
    "close_app": lambda app, **_: _close_app(app),
    "open_url": lambda url, **_: _open_url(url),
    "open_browser": lambda app="chrome", **_: _open_app(app),

    "create_file": create_file,
    "delete_file": delete_file,
    "search_web": search_web_tool,

    "volume_up": _optional(volume_up),
    "volume_down": _optional(volume_down),
    "mute": _optional(mute_volume),
    "unmute": _optional(unmute),

    "shutdown_pc": _optional(shutdown_pc),
    "restart_pc": _optional(restart_pc),
    "sleep_pc": _optional(sleep_pc),
    "lock_pc": _optional(lock_pc),

    # System
    "screenshot": lambda **_: execute({"intent": "screenshot"}),
    "brightness_up": lambda **_: execute({"intent": "brightness_up"}),
    "brightness_down": lambda **_: execute({"intent": "brightness_down"}),
    "lock": lambda **_: execute({"intent": "lock"}),
    "sleep": lambda **_: execute({"intent": "sleep"}),
    "shutdown": lambda **_: execute({"intent": "shutdown"}),
    "restart": lambda **_: execute({"intent": "restart"}),
    "wifi_on": lambda **_: execute({"intent": "wifi_on"}),
    "wifi_off": lambda **_: execute({"intent": "wifi_off"}),
    "empty_trash": lambda **_: execute({"intent": "empty_trash"}),

    # Info
    "query_time": lambda **_: execute({"intent": "query_time"}),
    "query_date": lambda **_: execute({"intent": "query_date"}),
    "query_battery": lambda **_: execute({"intent": "query_battery"}),
    "query_ram": lambda **_: execute({"intent": "query_ram"}),

    # AI fallback
    "ask_claude": lambda text, **_: execute({"intent": "ask_claude", "text": text}),
    "exit": lambda **_: execute({"intent": "exit"}),
}
