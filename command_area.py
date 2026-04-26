def normalize_command(text):

    if not text:
        return ""

    c = text.lower().strip()

    replacements = {

        "shut down": "shutdown",
        "shut-down": "shutdown",

        "un mute": "unmute",
        "un-mute": "unmute",

        "turn off volume": "volume down",
        "lower volume": "volume down",

        "turn up volume": "volume up",
        "increase volume": "volume up",
    }

    for key, value in replacements.items():
        c = c.replace(key, value)

    return c


def parse_command(command):
    if not command or not command.strip():
        return None  # Ensure we don’t proceed with an empty command

    # c = command.lower().strip()
    c = normalize_command(command)

    if c.startswith("open "):
        return {"type": "open_app", "target": c.replace("open ", "")}

    if c.startswith("close "):
        return {"type": "close_app", "target": c.replace("close ", "")}

    if c.startswith("create "):
        return {"type": "create_file", "target": c.replace("create ", "")}

    if c.startswith("delete "):
        return {"type": "delete_file", "target": c.replace("delete ", "")}

    if "search" in c:
        return {"type": "search_web", "target": c.replace("search", "").strip()}

    if "volume up" in c:
        return {"type": "volume_up"}

    if "volume down" in c:
        return {"type": "volume_down"}

    if c == "mute":
        return {"type": "mute"}

    if c == "unmute":
        return {"type": "unmute"}
    
    if "open whatsapp" in c:
        return {"type": "open_whatsapp"}
    
    if "shutdown" in c:
        return {"type": "shutdown_pc"}

    if "sleep" in c:
        return {"type": "sleep_pc"}    

    if "lock" in c:
        return {"type": "lock_pc"}  
      
    if "restart" in c:
        return {"type": "restart_pc"}
   
    if "send message" in c:
        text = c.replace("send message", "").strip()
        parts = text.split(" ", 1)
        if len(parts) < 2:
            return None
        return {
            "type": "send_message",
            "target": parts[0],
            "message": parts[1]
        }

    return None