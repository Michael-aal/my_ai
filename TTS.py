import requests

api_key = "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"
url = "https://api.openai.com/v1/audio/speak"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "input": "Hello, this is a test of the text-to-speech system.",
    "voice": "en-US-Wavenet-D",  # You can pick different voices
    "model": "tts-1"  # Check OpenAI docs for exact model name
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("Audio saved as output.mp3")
else:
    print(f"Error: {response.status_code} - {response.text}")