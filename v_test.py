# """
# test_intent_parser.py
# ─────────────────────
# Run with:  python test_intent_parser.py
# All tests must pass before shipping.
# """

# from intent_parser import detect_intent

# PASS = "\033[92m PASS\033[0m"
# FAIL = "\033[91m FAIL\033[0m"

# tests = [
#     # ── WhatsApp ──────────────────────────────────────────────────────────────
#     ("send message to john hey there",          {"intent": "send_whatsapp", "name": "john",    "message": "hey there"}),
#     ("send a whatsapp message to alice hello",  {"intent": "send_whatsapp", "name": "alice",   "message": "hello"}),
#     ("whatsapp bob say I'm on my way",          {"intent": "send_whatsapp", "name": "bob",     "message": "i'm on my way"}),

#     # ── URL open ──────────────────────────────────────────────────────────────
#     ("open youtube.com",                        {"intent": "open_url", "url": "https://youtube.com"}),
#     ("go to google.com",                        {"intent": "open_url", "url": "https://google.com"}),
#     ("visit https://github.com",                {"intent": "open_url", "url": "https://github.com"}),
#     ("youtube.com",                             {"intent": "open_url", "url": "https://youtube.com"}),

#     # ── App open ──────────────────────────────────────────────────────────────
#     ("open chrome",                             {"intent": "open_app", "app": "chrome"}),
#     ("open google chrome browser",              {"intent": "open_app", "app": "chrome"}),
#     ("launch vs code",                          {"intent": "open_app", "app": "vscode"}),
#     ("start vlc media player",                  {"intent": "open_app", "app": "vlc"}),
#     ("run notepad",                             {"intent": "open_app", "app": "notepad"}),
#     ("open file explorer",                      {"intent": "open_app", "app": "explorer"}),

#     # ── App close ─────────────────────────────────────────────────────────────
#     ("close chrome",                            {"intent": "close_app", "app": "chrome"}),
#     ("kill notepad",                            {"intent": "close_app", "app": "notepad"}),
#     ("quit vlc",                                {"intent": "close_app", "app": "vlc"}),

#     # ── Web search ────────────────────────────────────────────────────────────
#     ("search python tutorials",                 {"intent": "open_url", "url": "https://www.google.com/search?q=python+tutorials"}),
#     ("google what is machine learning",         {"intent": "open_url", "url": "https://www.google.com/search?q=what+is+machine+learning"}),

#     # ── File ops ──────────────────────────────────────────────────────────────
#     ("create file notes.txt",                   {"intent": "create_file", "filename": "notes.txt"}),
#     ("make a new file report.docx",             {"intent": "create_file", "filename": "report.docx"}),
#     ("delete file old.txt",                     {"intent": "delete_file", "filename": "old.txt"}),

#     # ── Memory ────────────────────────────────────────────────────────────────
#     ("remember my name is Alex",                {"intent": "memory_save", "key": "name",     "value": "alex"}),
#     ("what is my name",                         {"intent": "memory_recall", "key": "name"}),
#     ("what's my browser",                       {"intent": "memory_recall", "key": "browser"}),
#     ("forget my password",                      {"intent": "memory_forget", "key": "password"}),

#     # ── Screenshot ────────────────────────────────────────────────────────────
#     ("take a screenshot",                       {"intent": "screenshot"}),
#     ("screenshot",                              {"intent": "screenshot"}),

#     # ── Audio ─────────────────────────────────────────────────────────────────
#     ("mute",                                    {"intent": "mute"}),
#     ("unmute",                                  {"intent": "unmute"}),
#     ("volume up",                               {"intent": "volume_up"}),
#     ("louder",                                  {"intent": "volume_up"}),
#     ("volume down",                             {"intent": "volume_down"}),
#     ("turn down",                               {"intent": "volume_down"}),

#     # ── Brightness ────────────────────────────────────────────────────────────
#     ("brighter",                                {"intent": "brightness_up"}),
#     ("dimmer",                                  {"intent": "brightness_down"}),

#     # ── WiFi ──────────────────────────────────────────────────────────────────
#     ("wifi on",                                 {"intent": "wifi_on"}),
#     ("turn off wifi",                           {"intent": "wifi_off"}),

#     # ── System info ───────────────────────────────────────────────────────────
#     ("what time is it",                         {"intent": "query_time"}),
#     ("what's the date",                         {"intent": "query_date"}),
#     ("battery level",                           {"intent": "query_battery"}),
#     ("how much ram",                            {"intent": "query_ram"}),

#     # ── Power ─────────────────────────────────────────────────────────────────
#     ("lock screen",                             {"intent": "lock"}),
#     ("go to sleep",                             {"intent": "sleep"}),
#     ("restart",                                 {"intent": "restart"}),
#     ("shutdown",                                {"intent": "shutdown"}),
#     ("shut down",                               {"intent": "shutdown"}),
#     ("power off",                               {"intent": "shutdown"}),

#     # ── No bleed: "search restart methods" must NOT trigger restart ───────────
#     ("search restart methods",                  {"intent": "open_url"}),   # partial check

#     # ── Misc ──────────────────────────────────────────────────────────────────
#     ("empty trash",                             {"intent": "empty_trash"}),
#     ("goodbye",                                 {"intent": "exit"}),

#     # ── Fallback ──────────────────────────────────────────────────────────────
#     ("who is the president of nigeria",         {"intent": "ask_claude"}),
# ]


# def _match(result: dict, expected: dict) -> bool:
#     for k, v in expected.items():
#         if result.get(k) != v:
#             # For partial checks (only intent key supplied), allow it
#             if k == "intent" and result.get(k) != v:
#                 return False
#             if k != "intent":
#                 return False
#     return True


# passed = failed = 0
# for cmd, expected in tests:
#     result = detect_intent(cmd)
#     ok = _match(result, expected)
#     symbol = PASS if ok else FAIL
#     print(f"{symbol}  [{cmd!r}]")
#     if not ok:
#         print(f"        expected: {expected}")
#         print(f"        got:      {result}")
#     passed += ok
#     failed += not ok

# print(f"\n{'='*50}")
# print(f"  {passed}/{passed+failed} passed  |  {failed} failed")


import threading

# Global flag to track if AI is speaking
is_speaking = False

def speak(text):
    global is_speaking
    is_speaking = True
    # Existing TTS logic here
    print(f"[AI] {text}")
    # After TTS is done, reset the flag
    is_speaking = False

def interrupt():
    global is_speaking
    if is_speaking:
        # Insert your TTS stop logic here (if supported by your TTS engine)
        is_speaking = False
        print("AI interrupted, ready to listen again.")

def handle_command(text: str):
    text = strip_wake_word(text)
    if not text:
        return

    print(f'\n[ARIA] Heard: "{text}"')

    # Interrupt if speaking before a new command
    if is_speaking:
        interrupt()

    t = text  # alias

    # Existing command checks
    if any(x in t for x in ["open chrome", "launch chrome"]):
        print("  Opening Chrome")
        _open_app("google-chrome", "Google Chrome", "chrome")
    elif any(x in t for x in ["open terminal", "launch terminal"]):
        print("  Opening Terminal")
        _open_app("x-terminal-emulator", "Terminal", "cmd")
    # ... (all other command checks remain the same)

    elif any(x in t for x in ["stop", "quit", "exit", "goodbye", "bye aria"]):
        print("  Goodbye!")
        sys.exit(0)

    else:
        _ask_claude(text)

# Main loop stays the same
def main():
    # ... (same as before)
    while True:
        try:
            audio = record_utterance()

            if audio is None:
                continue

            if rms(audio) < SILENCE_THRESHOLD * 0.05:
                continue

            print("[transcribing...]", end="\r")
            text = transcribe(audio)

            if not text:
                continue

            if WAKE_WORD_MODE:
                if contains_wake_word(text):
                    handle_command(text)
                else:
                    print(f'[standby] "{text}"')
            else:
                handle_command(text)

        except KeyboardInterrupt:
            print("\n\nARIA stopped. Goodbye!")
            break
        except Exception as e:
            print(f"[error] {e}")
            time.sleep(0.3)

if __name__ == "__main__":
    main()