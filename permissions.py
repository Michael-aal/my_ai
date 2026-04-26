# permissions.py
import json, os, hashlib

PERMISSIONS_FILE = os.path.join(os.path.expanduser("~"), ".jarvis_permissions.json")

_DEFAULTS = {
    "app_control": None,   # None = not yet asked
    "system_control": None,
}

def _load() -> dict:
    if not os.path.exists(PERMISSIONS_FILE):
        return dict(_DEFAULTS)
    with open(PERMISSIONS_FILE) as f:
        return json.load(f)

def _save(perms: dict):
    # Write atomically
    tmp = PERMISSIONS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(perms, f, indent=2)
    os.replace(tmp, PERMISSIONS_FILE)

def prompt_first_run():
    """Call once at startup. Asks for any unset permissions."""
    perms = _load()
    changed = False

    if perms.get("app_control") is None:
        print("\n[Jarvis Setup] May Jarvis open and close applications on your computer?")
        ans = input("  Type 'yes' to allow, anything else to deny: ").strip().lower()
        perms["app_control"] = (ans == "yes")
        changed = True

    if perms.get("system_control") is None:
        print("\n[Jarvis Setup] May Jarvis perform system actions (shutdown, restart, sleep)?")
        ans = input("  Type 'yes' to allow, anything else to deny: ").strip().lower()
        perms["system_control"] = (ans == "yes")
        changed = True

    if changed:
        _save(perms)
        print("\n[Jarvis] Permissions saved. You can edit ~/.jarvis_permissions.json to change them.\n")

    return perms

def is_allowed(permission: str) -> bool:
    perms = _load()
    return perms.get(permission, False) is True