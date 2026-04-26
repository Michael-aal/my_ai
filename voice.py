import asyncio
import edge_tts
import pygame
import threading
import os
import uuid

VOICE = "en-ZA-LukeNeural"

# Folder to store audio files
AUDIO_FOLDER = "audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Set to False if you want to KEEP all audio files
AUTO_DELETE = True

_is_speaking = False
_lock = threading.Lock()


async def generate_audio(text, filename):
    communicate = edge_tts.Communicate(str(text), VOICE)
    await communicate.save(filename)


def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue


def speak(text):
    global _is_speaking

    with _lock:
        _is_speaking = True

    def run():
        try:
            # Save inside audio folder with unique name
            filename = os.path.join(
                AUDIO_FOLDER,
                f"speech_{uuid.uuid4().hex}.mp3"
            )

            asyncio.run(generate_audio(text, filename))
            play_audio(filename)

            # Delete after playing (optional)
            if AUTO_DELETE:
                try:
                    os.remove(filename)
                except:
                    pass

        finally:
            global _is_speaking
            with _lock:
                _is_speaking = False

    threading.Thread(target=run, daemon=True).start()


def is_speaking():
    return _is_speaking