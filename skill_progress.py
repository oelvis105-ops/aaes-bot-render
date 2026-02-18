import os
import json

PATH = "data/skill_progress.json"


def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({}, f)


def load_progress():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_progress(data):
    _init()
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


def set_last_lesson(user_id: int, skill_key: str, lesson_number: int):
    data = load_progress()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {}
    data[uid][skill_key] = lesson_number
    save_progress(data)


def get_last_lesson(user_id: int, skill_key: str) -> int:
    data = load_progress()
    uid = str(user_id)
    return data.get(uid, {}).get(skill_key, 0)


def clear_progress(user_id: int, skill_key: str = None):
    data = load_progress()
    uid = str(user_id)
    if uid not in data:
        return
    if skill_key:
        data[uid].pop(skill_key, None)
    else:
        data.pop(uid, None)
    save_progress(data)
