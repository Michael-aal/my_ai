def parse_command(command):

    c = command.lower().strip()

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
   
    if "send whatsapp" in c:

      text = c.replace("send whatsapp", "").strip()
      parts = text.split(" ", 1)

      if len(parts) < 2:
              return None

      return {
            "type": "send_whatsapp",
            "target": parts[0],
            "message": parts[1]
        }

    return None


def open_app(name):
    import os, webbrowser

    apps = load_apps()
    name = name.lower()

    if name in apps:
        path = apps[name]

        if path.startswith("http"):
            webbrowser.open(path)
        else:
            os.startfile(path)

        return f"Opening {name}"

    os.system(f"start {name}")
    return f"Tried opening {name}"