import os


def open_folder(path):
    try:
        if os.path.exists(path):
            os.startfile(path)
            return f"Opened folder: {path}"
        return "Folder not found"
    except Exception as e:
        return str(e)


def create_file(name):
    try:
        with open(name, "w") as f:
            f.write("")
        return f"{name} created"
    except Exception as e:
        return str(e)


def delete_file(name):
    try:
        if os.path.exists(name):
            os.remove(name)
            return f"{name} deleted"
        return "File not found"
    except Exception as e:
        return str(e)


def list_files(path="."):
    try:
        return os.listdir(path)
    except Exception as e:
        return str(e)