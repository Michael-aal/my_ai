# import json
# import webbrowser
# from urllib.parse import quote

# import os

# CONTACT_FILE = os.path.join("memory", "contacts.json")

# def load_contacts():

#     with open(CONTACT_FILE, "r") as file:
#         return json.load(file)


# def send_whatsapp_message(name, message):

#     contacts = load_contacts()

#     name = name.lower()

#     if name not in contacts:
#         return f"I don't know {name}'s number yet."

#     number = contacts[name]

#     encoded_message = quote(message)

#     url = f"https://wa.me/{number}?text={encoded_message}"

#     webbrowser.open(url)

#     return f"Opening WhatsApp chat with {name}"

import pyautogui
import time


def open_whatsapp():
    pyautogui.hotkey("win")
    time.sleep(1)
    pyautogui.write("whatsapp")
    time.sleep(1)
    pyautogui.press("enter")
    return "Opening WhatsApp"


def send_message(contact, message):
    open_whatsapp()
    time.sleep(5)

    # search contact
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)
    pyautogui.write(contact)
    time.sleep(2)
    pyautogui.press("down")
    pyautogui.press("enter")

    # type message
    time.sleep(2)
    pyautogui.write(message)
    pyautogui.press("enter")

    return f"Message sent to {contact}"