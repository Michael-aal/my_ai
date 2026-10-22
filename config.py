ASSISTANT_NAME = "jarvis"

WAKE_WORD = "jarvis"

MODEL_NAME = "base"

VOICE_RATE = 180

MIC_DURATION = 3





import os

try:
    from Encryptor import encrypt, decrypt
except ImportError:
    encrypt = decrypt = None

SECRET_FILE = "storage/.secret"


class SecureConfig:
    def __init__(self):
        self.api_key = self.load_api_key()

    # -------------------------
    # 1. ENV LOADER (priority)
    # -------------------------
    def from_env(self):
        return os.getenv("GEMINI_API_KEY")

    # -------------------------
    # 2. ENCRYPTED FILE STORAGE
    # -------------------------
    def save_encrypted(self, key: str):
        if encrypt is None:
            raise RuntimeError("cryptography not installed — cannot encrypt key")
        encrypted = encrypt(key)

        os.makedirs("storage", exist_ok=True)
        with open(SECRET_FILE, "wb") as f:
            f.write(encrypted)

    def load_encrypted(self):
        if decrypt is None or not os.path.exists(SECRET_FILE):
            return None

        with open(SECRET_FILE, "rb") as f:
            encrypted = f.read()

        return decrypt(encrypted)

    # -------------------------
    # 3. MAIN RESOLVER
    # -------------------------
    def load_api_key(self):
        # Priority 1: environment variable
        key = self.from_env()
        if key:
            return key

        # Priority 2: encrypted local file
        key = self.load_encrypted()
        if key:
            return key

        return None

    # -------------------------
    # 4. VALIDATION
    # -------------------------
    def get_key(self):
        if not self.api_key:
            raise ValueError(
                "No API key found. Set GEMINI_API_KEY or store encrypted key."
            )
        return self.api_key