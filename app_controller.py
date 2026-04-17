import os



def open_app(app):

    apps = {
        "calculator": "calc",
        "notepad": "notepad",
        "chrome": "start chrome",
        "paint": "mspaint.exe",

  "vscode": "C:\\Users\\austi\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",

  "whatsapp": "https://web.whatsapp.com",

  "telegram": "C:\\Users\\austi\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe"

    }

    if app in apps:
        os.system(apps[app])



def close_app(app):

    processes = {
        "calculator": "Calculator.exe",
        "notepad": "notepad.exe",
        "chrome": "chrome.exe"
    }

    if app in processes:
        os.system(f"taskkill /f /im {processes[app]}")