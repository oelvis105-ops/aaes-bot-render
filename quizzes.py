import json
import os
import random
from datetime import datetime


PATH = "data/quizzes.json"
HISTORY_PATH = "data/quiz_history.json"


def ensure_files():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({"general": [], "aero": [], "auto": [], "marine": []}, f)

    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w") as f:
            json.dump({}, f)


def load_quizzes():
    ensure_files()
    with open(PATH, "r") as f:
        return json.load(f)


def save_quizzes(qz):
    with open(PATH, "w") as f:
        json.dump(qz, f, indent=4)


def load_history():
    ensure_files()
    with open(HISTORY_PATH, "r") as f:
        return json.load(f)


def save_history(data):
    with open(HISTORY_PATH, "w") as f:
        json.dump(data, f, indent=4)


def add_quiz(category, question, answer):
    qz = load_quizzes()
    if category not in qz:
        qz[category] = []

    qz[category].append({"question": question, "answer": answer})
    save_quizzes(qz)
    return True


def random_quiz(category="general"):
    qz = load_quizzes()

    if category not in qz or not qz[category]:
        return None

    return random.choice(qz[category])


def log_quiz_attempt(user_id, correct):
    data = load_history()

    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "attempts": 0,
            "correct": 0,
            "last_active": None
        }

    data[uid]["attempts"] += 1
    if correct:
        data[uid]["correct"] += 1

    data[uid]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_history(data)


def get_user_quiz_stats(user_id):
    data = load_history()
    return data.get(str(user_id), {
        "attempts": 0,
        "correct": 0,
        "last_active": None
    })


def generate_exam_mode_question():
    qz = load_quizzes()

    pool = []
    for cat in ["general", "aero", "auto", "marine"]:
        pool.extend(qz.get(cat, []))

    if not pool:
        return None

    return random.choice(pool)
