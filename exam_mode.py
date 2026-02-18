import os
import json
from datetime import datetime, timedelta
import random

PATH = "data/exam_mode.json"

# ----------------------------------------------------
# Initialize storage
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({
                "active": False,
                "exam_date": "",
                "last_quiz_sent": "",
                "quizzes": []
            }, f)


# ----------------------------------------------------
# Load / Save
# ----------------------------------------------------
def load_exam():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_exam(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Activate Exam Mode (Admin Only)
# ----------------------------------------------------
def activate_exam_mode(exam_date_str):
    """
    exam_date_str format: YYYY-MM-DD
    Example: 2025-05-10
    """
    data = load_exam()
    data["active"] = True
    data["exam_date"] = exam_date_str
    save_exam(data)
    return True


# ----------------------------------------------------
# Deactivate Exam Mode
# ----------------------------------------------------
def deactivate_exam_mode():
    data = load_exam()
    data["active"] = False
    data["exam_date"] = ""
    save_exam(data)
    return True


# ----------------------------------------------------
# Check if active
# ----------------------------------------------------
def exam_mode_active():
    return load_exam().get("active", False)


# ----------------------------------------------------
# Countdown Engine
# ----------------------------------------------------
def exam_countdown():
    data = load_exam()

    if not data["active"] or not data["exam_date"]:
        return None

    today = datetime.now().date()
    exam_date = datetime.fromisoformat(data["exam_date"]).date()
    days_left = (exam_date - today).days

    if days_left < 0:
        return None

    return days_left


# ----------------------------------------------------
# Quiz System
# ----------------------------------------------------
DEFAULT_QUIZZES = [
    "Explain Bernoulli’s principle in one sentence.",
    "What is the difference between laminar and turbulent flow?",
    "Define tensile strength.",
    "What is cavitation in marine propellers?",
    "What does the compression ratio mean in engines?",
    "Why do airplanes need flaps during landing?",
    "Explain drag in simple terms.",
    "Define torque.",
    "Why do ships use ballast tanks?",
    "State Newton’s Third Law."
]


def get_daily_quiz():
    data = load_exam()

    quizzes = data.get("quizzes", [])
    if not quizzes:
        quizzes = DEFAULT_QUIZZES

    return random.choice(quizzes)


def add_quiz(question):
    data = load_exam()
    if "quizzes" not in data:
        data["quizzes"] = []

    data["quizzes"].append(question)
    save_exam(data)
    return True


# ----------------------------------------------------
# Prevent double sending per day
# ----------------------------------------------------
def should_send_quiz_today():
    data = load_exam()
    today = str(datetime.now().date())
    return data.get("last_quiz_sent", "") != today


def mark_quiz_sent():
    data = load_exam()
    data["last_quiz_sent"] = str(datetime.now().date())
    save_exam(data)
