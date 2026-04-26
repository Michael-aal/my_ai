from cryptography.fernet import Fernet
import os

KEY_PATH = "storage/.key"


# -------------------------
# SAFE KEY GENERATION
# -------------------------
def get_or_create_key():
    os.makedirs("storage", exist_ok=True)

    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            key = f.read()

        # validate key
        try:
            Fernet(key)
            return key
        except Exception:
            pass  # corrupted key → regenerate

    # generate fresh valid key
    key = Fernet.generate_key()

    with open(KEY_PATH, "wb") as f:
        f.write(key)

    return key


# -------------------------
# ENCRYPT
# -------------------------
def encrypt(text: str) -> bytes:
    key = get_or_create_key()
    f = Fernet(key)
    return f.encrypt(text.encode())


# -------------------------
# DECRYPT
# -------------------------
def decrypt(token: bytes) -> str:
    key = get_or_create_key()
    f = Fernet(key)
    return f.decrypt(token).decode()