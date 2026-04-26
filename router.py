from listener import record_utterance, transcribe, contains_wake_word, strip_wake_word
from intent_engine import detect_intent
from action_engine import perform_action
from voice import speak, is_speaking
from database import set_info, get_info, get_all_info
from permissions import prompt_first_run

import traceback

WAKE_WORD_MODE = True
active = False
DEBUG = True


# ─────────────────────────────────────────
# MEMORY SYSTEM
# ─────────────────────────────────────────
def memory_commands(text):
    text = text.lower().strip()

    # STORE MEMORY
    if text.startswith("remember"):
        try:
            clean = text.replace("remember", "").strip()
            key, value = clean.split(" is ")
            set_info(key.strip(), value.strip())
            return f"Saved {key}"

        except Exception:
            return "I did not understand"

    # RETRIEVE MEMORY
    if text.startswith("what is"):
        key = text.replace("what is", "").strip()
        value = get_info(key)
        return value if value else "No data found"

    # SHOW ALL MEMORY
    if "show memory" in text:
        return str(get_all_info())

    return None


# ─────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────
def run_assistant():
    global active

    prompt_first_run()  # First-time permission prompt

    print("Jarvis ready... Listening")

    while True:
        try:
            # ── BLOCK DURING SPEECH ───────────────
            if is_speaking():
                continue

            if DEBUG:
                print("\n[WAITING FOR SPEECH]")

            audio = record_utterance()

            if audio is None:
                if DEBUG:
                    print("[NO AUDIO CAPTURED]")
                continue

            # ── TRANSCRIPTION ─────────────────────
            if DEBUG:
                print("[TRANSCRIBING...]")

            text = transcribe(audio)

            if DEBUG:
                print("RAW TEXT:", text)

            # ── HARD FAIL SAFE ────────────────────
            if not text or not isinstance(text, str) or not text.strip():
                if DEBUG:
                    print("[INVALID TRANSCRIPTION]")
                continue

            text = text.lower().strip()

            # ── WAKE WORD SYSTEM ───────────────────
            if WAKE_WORD_MODE:
                if not active:
                    if contains_wake_word(text):
                        active = True
                        speak("Yes. I am listening.")
                    continue

            # REMOVE WAKE WORD
            text = strip_wake_word(text)

            # ── SLEEP COMMAND ─────────────────────
            if any(x in text for x in ["go to sleep", "bye", "dismiss"]):
                active = False
                speak("Going offline")
                continue

            # ── MEMORY FAST PATH ──────────────────
            memory_response = memory_commands(text)

            if memory_response:
                print("Jarvis:", memory_response)
                speak(memory_response)
                continue

            # ── INTENT ENGINE ─────────────────────
            if DEBUG:
                print("[DETECTING INTENT...]")

            intent = detect_intent(text)

            if DEBUG:
                print("INTENT:", intent)

            # HARD VALIDATION
            if not isinstance(intent, dict) or "intent" not in intent:
                speak("I could not understand the command")
                continue

            # ── ACTION ENGINE ─────────────────────
            output = perform_action(intent)

            if DEBUG:
                print("OUTPUT:", output)

            if not output:
                output = "I did not get that"

            speak(output)

        except Exception as e:
            traceback.print_exc()
            print("Router Error:", e)
            speak("System error occurred")