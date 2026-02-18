import os
import json

PATH = "data/subscribers.json"

def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump([], f)

def load_subscribers():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)

def save_subscribers(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)

def subscribe(user_id):
    data = load_subscribers()

    uid = str(user_id)

    if uid not in data:
        data.append(uid)
        save_subscribers(data)

def unsubscribe(user_id):
    data = load_subscribers()
    uid = str(user_id)

    if uid in data:
        data.remove(uid)
        save_subscribers(data)

def list_subscribers():
    return load_subscribers()
