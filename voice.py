import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 170)


def speak(text):

    if not text:
        return

    engine.say(text)
    engine.runAndWait()