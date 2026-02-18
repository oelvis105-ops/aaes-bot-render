import os
import json

PATH = "data/profiles.json"

def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({}, f)

def load_profiles():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)

def save_profiles(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_profile(user_id):
    _init()
    data = load_profiles()

    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "name": "unknown",
            "program": "None",
            "level": "NONE",
            "recent": []
        }
        save_profiles(data)
        
    return data[uid]

def update_profile(user_id, field, value):
    data = load_profiles()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {}
    
    data[uid][field] = value
    save_profiles(data)

def log_question(user_id, question):
    data = load_profiles()

    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "name": "unknown",
            "program": "None",
            "level": "NONE",
            "recent": []
        }
    if "recent" not in data[uid]:
        data[uid]["recent"] = []

    data[uid]["recent"].append(question)
    data[uid]["recent"] = data[uid]["recent"][-5:]

    save_profiles(data)

