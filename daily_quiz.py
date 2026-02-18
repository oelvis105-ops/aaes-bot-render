import os
import json
import random
from datetime import datetime
from exam_mode import exam_mode_active

PATH = "data/daily_quiz.json"

# ----------------------------------------------------
# Initialise storage
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({
                "questions": [],
                "last_sent": "",
                "last_question": ""
            }, f)


# ----------------------------------------------------
# Load / Save
# ----------------------------------------------------
def load_quiz():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_quiz(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Default question pool (placeholder)
# ----------------------------------------------------
DEFAULT_QUESTIONS = [
    "Aerospace: What is the purpose of an airfoil?",
    "Auto: What does RPM measure in an engine?",
    "Marine: Why do ships use displacement hulls?",
    "Aerospace: What force counteracts gravity during flight?",
    "Auto: What is the function of a catalytic converter?",
    "Marine: What material is most ship hull plating made of?",
    "Aerospace: What is stall speed?",
    "Auto: What happens when an engine runs too lean?",
    "Marine: What keeps a submarine neutral underwater?"
]


# ----------------------------------------------------
# Get today's question
# ----------------------------------------------------
def get_daily_quiz():
    data = load_quiz()

    if not data["questions"]:
        data["questions"] = DEFAULT_QUESTIONS

    questions = data["questions"]

    # Remove last question to prevent duplicates
    last_q = data.get("last_question", "")
    if last_q in questions and len(questions) > 1:
        filtered = [q for q in questions if q != last_q]
    else:
        filtered = questions

    chosen = random.choice(filtered)

    # Save last question
    data["last_question"] = chosen
    save_quiz(data)

    return chosen


# ----------------------------------------------------
# Should the bot send today's quiz?
# ----------------------------------------------------
def should_send_quiz():
    if not exam_mode_active():
        return False

    data = load_quiz()
    today = str(datetime.now().date())

    return data.get("last_sent", "") != today


def mark_quiz_sent():
    data = load_quiz()
    data["last_sent"] = str(datetime.now().date())
    save_quiz(data)


# ----------------------------------------------------
# Add a new quiz question
# ----------------------------------------------------
def add_quiz(question):
    data = load_quiz()
    data["questions"].append(question)
    save_quiz(data)
    return True
