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

from whatsapp_bot import open_whatsapp, send_message
from file_controller import create_file, delete_file
from web_controller import search_web_tool
from system_control import volume_up, volume_down, mute_volume, unmute, shutdown_pc, sleep_pc , restart_pc, lock_pc
from tools import open_app, close_app  # OK because now tools handles it

TOOLS = {
   "open_whatsapp": open_whatsapp,
    "send_message": send_message,


    "open_app": open_app,
    "close_app": close_app,

    "create_file": create_file,
    "delete_file": delete_file,

    "search_web": search_web_tool,

    "volume_up": volume_up,
    "volume_down": volume_down,
    "mute": mute_volume,
    "unmute": unmute,

    "shutdown_pc": shutdown_pc,
    "restart_pc": restart_pc,
    "sleep_pc": sleep_pc,
    "lock_pc": lock_pc

}


"""
tools.py
────────
All callable tools keyed by action string.
Used by action_engine.execute() via intent dispatch.
"""

from action_engine import (
    _open_app,
    _close_app,
    _open_url,
    execute,
)

# Re-export so callers can do: from tools import TOOLS
TOOLS = {
    "open_app":       lambda app, **_:     _open_app(app),
    "close_app":      lambda app, **_:     _close_app(app),
    "open_url":       lambda url, **_:     _open_url(url),
    "open_browser":   lambda app="chrome", **_: _open_app(app),

    # System
    "screenshot":     lambda **_:          execute({"intent": "screenshot"}),
    "mute":           lambda **_:          execute({"intent": "mute"}),
    "unmute":         lambda **_:          execute({"intent": "unmute"}),
    "volume_up":      lambda **_:          execute({"intent": "volume_up"}),
    "volume_down":    lambda **_:          execute({"intent": "volume_down"}),
    "brightness_up":  lambda **_:          execute({"intent": "brightness_up"}),
    "brightness_down":lambda **_:          execute({"intent": "brightness_down"}),
    "lock":           lambda **_:          execute({"intent": "lock"}),
    "sleep":          lambda **_:          execute({"intent": "sleep"}),
    "shutdown":       lambda **_:          execute({"intent": "shutdown"}),
    "restart":        lambda **_:          execute({"intent": "restart"}),
    "wifi_on":        lambda **_:          execute({"intent": "wifi_on"}),
    "wifi_off":       lambda **_:          execute({"intent": "wifi_off"}),
    "empty_trash":    lambda **_:          execute({"intent": "empty_trash"}),

    # Info
    "query_time":     lambda **_:          execute({"intent": "query_time"}),
    "query_date":     lambda **_:          execute({"intent": "query_date"}),
    "query_battery":  lambda **_:          execute({"intent": "query_battery"}),
    "query_ram":      lambda **_:          execute({"intent": "query_ram"}),

    # AI fallback
    "ask_claude":     lambda text, **_:    execute({"intent": "ask_claude", "text": text}),
    "exit":           lambda **_:          execute({"intent": "exit"}),
}