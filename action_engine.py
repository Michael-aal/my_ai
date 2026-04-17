from tools import TOOLS


def perform_action(action):

    if not action:
        return "No action received"

    action_type = action.get("type")

    if action_type not in TOOLS:
        return f"Unknown action: {action_type}"

    tool = TOOLS[action_type]

    try:

        # support full parameter system (V4-ready)
        if "params" in action:
            result = tool(**action["params"])

        elif "message" in action and "target" in action:
            result = tool(action["target"], action["message"])

        elif "target" in action:
            result = tool(action["target"])

        else:
            result = tool()

        # guarantee speech output
        if not result:
            target = action.get("target", "action")
            return f"{target} executed successfully"

        return result

    except Exception as e:
        return f"Action failed: {str(e)}"
    