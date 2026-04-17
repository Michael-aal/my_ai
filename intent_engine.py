def detect_intent(text):

    text = text.lower().strip()

    # -----------------------------
    # WHATSAPP AUTOMATION
    # -----------------------------
    if "send message to" in text:

        parts = text.replace("send message to", "").strip().split(" ", 1)

        if len(parts) < 2:
            return {
                "tool": "fallback",
                "params": {"text": text}
            }

        name = parts[0]
        message = parts[1]

        return {
            "tool": "send_whatsapp",
            "params": {
                "name": name,
                "message": message
            }
        }

    # -----------------------------
    # OPEN APPLICATION
    # -----------------------------
    if text.startswith("open "):

        app_name = text.replace("open ", "").strip()

        return {
            "tool": "open_app",
            "params": {"name": app_name}
        }

    # -----------------------------
    # CLOSE APPLICATION
    # -----------------------------
    if text.startswith("close "):

        app_name = text.replace("close ", "").strip()

        return {
            "tool": "close_app",
            "params": {"name": app_name}
        }

    # -----------------------------
    # WEB SEARCH
    # -----------------------------
    if text.startswith("search "):

        query = text.replace("search ", "").strip()

        return {
            "tool": "search_web",
            "params": {"query": query}
        }

    # -----------------------------
    # CREATE FILE
    # -----------------------------
    if text.startswith("create file "):

        filename = text.replace("create file ", "").strip()

        return {
            "tool": "create_file",
            "params": {"filename": filename}
        }

    # -----------------------------
    # DELETE FILE
    # -----------------------------
    if text.startswith("delete file "):

        filename = text.replace("delete file ", "").strip()

        return {
            "tool": "delete_file",
            "params": {"filename": filename}
        }

    # -----------------------------
    # MEMORY STORE
    # -----------------------------
    if text.startswith("remember "):

        content = text.replace("remember ", "").strip()

        return {
            "tool": "remember",
            "params": {"content": content}
        }

    # -----------------------------
    # MEMORY RECALL
    # -----------------------------
    if text.startswith("what is my"):

        key = text.replace("what is my", "").strip()

        return {
            "tool": "recall",
            "params": {"key": key}
        }

    # -----------------------------
    # SYSTEM SHUTDOWN
    # -----------------------------
    if "shutdown" in text:

        return {
            "tool": "shutdown",
            "params": {}
        }

    # -----------------------------
    # SYSTEM RESTART
    # -----------------------------
    if "restart" in text:

        return {
            "tool": "restart",
            "params": {}
        }

    # -----------------------------
    # FALLBACK (AI RESPONSE)
    # -----------------------------
    return {
        "tool": "fallback",
        "params": {"text": text}
    }