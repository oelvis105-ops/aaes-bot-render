import os
import json

PATH = "data/user_memory.json"


# ----------------------------------------------------
# Initialise storage
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({}, f)


# ----------------------------------------------------
# Load / Save
# ----------------------------------------------------
def load_memory():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Log a user interaction
# ----------------------------------------------------
def log_interaction(user_id, text):
    user_id = str(user_id)
    data = load_memory()

    if user_id not in data:
        data[user_id] = []

    data[user_id].append(text)

    # keep last 20 items
    data[user_id] = data[user_id][-20:]

    save_memory(data)


# ----------------------------------------------------
# Retrieve a user's past questions
# ----------------------------------------------------
def get_user_history(user_id):
    data = load_memory()
    user_id = str(user_id)

    if user_id not in data:
        return []

    return data[user_id]
