from textblob import TextBlob


def correct_spelling(text):
    if not text.strip():
        return ""

    corrected = str(TextBlob(text).correct())

    return corrected