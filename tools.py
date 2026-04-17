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
from system_control import volume_up, volume_down, mute_volume, unmute
from tools import open_app, close_app  # OK because now tools handles it

TOOLS = {
   "open_whatsapp": open_whatsapp,
    "send_whatsapp": send_message,


    "open_app": open_app,
    "close_app": close_app,

    "create_file": create_file,
    "delete_file": delete_file,

    "search_web": search_web_tool,

    "volume_up": volume_up,
    "volume_down": volume_down,
    "mute": mute_volume,
    "unmute": unmute
}