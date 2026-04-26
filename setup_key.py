from secure_config import SecureConfig

key = input("Enter your Gemini API key: ")

config = SecureConfig()
config.save_encrypted(key)

print("Key stored securely.")