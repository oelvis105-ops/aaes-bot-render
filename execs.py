import os
import json

PATH = "data/execs.json"


# ----------------------------------------------------
# Initialise storage
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump([], f)


# ----------------------------------------------------
# Load and save
# ----------------------------------------------------
def load_execs():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_execs(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Add a new executive
# ----------------------------------------------------
def add_exec(name, position, photo_url, phone=None, description=None):
    data = load_execs()

    entry = {
        "name": name,
        "position": position,
        "photo": photo_url,
        "phone": phone if phone else "",
        "description": description if description else ""
    }

    data.append(entry)
    save_execs(data)
    return True


# ----------------------------------------------------
# Remove an executive by index
# ----------------------------------------------------
def remove_exec(index):
    data = load_execs()

    if index < 0 or index >= len(data):
        return False

    removed = data.pop(index)
    save_execs(data)
    return removed

EXECS = [
    {"name": "President", "position": "President", "photo": "", "description": ""}
]

# ----------------------------------------------------
# Get list of all execs
# ----------------------------------------------------
def get_execs():
    return load_execs()


# ----------------------------------------------------
# Format output for Telegram
# ----------------------------------------------------
def format_exec_list():
    data = load_execs()

    if not data:
        return "No executive profiles available yet."

    out = "AAES Executive Board\n\n"

    for i, ex in enumerate(data):
        out += f"{i+1}. {ex['name']}\n"
        out += f"   Role: {ex['position']}\n"
        if ex["phone"]:
            out += f"   Phone: {ex['phone']}\n"
        if ex["description"]:
            out += f"   About: {ex['description']}\n"
        out += "\n"

    return out


# ----------------------------------------------------
# Get photo card format
# ----------------------------------------------------
def get_exec_photos():
    """
    Returns a list of dictionaries:
    [
        {"photo": "...", "caption": "..."},
        ...
    ]
    Useful for sending images in a carousel.
    """
    data = load_execs()
    out = []

    for ex in data:
        caption = f"{ex['name']}\n{ex['position']}"
        if ex["description"]:
            caption += f"\n\n{ex['description']}"

        out.append({
            "photo": ex["photo"],
            "caption": caption
        })

    return out
