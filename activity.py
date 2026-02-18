import os
import json

PATH = "data/activity.json"

def init_activity():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({}, f)
def load_activity():
    init_activity()
    with open(PATH, "r") as f:
        return json.load(f)

def save_activity(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)

def log_activity(user_id, text):
    data = load_activity()
    uid = str(user_id)
    if uid not in data:
        data[uid] = []
    data[uid].append(text)
    data[uid] = data[uid][-20:]

    save_activity(data)

def get_user_activity(user_id):
    data = load_activity()
    uid = str(user_id)
    return data.get(uid, [])
