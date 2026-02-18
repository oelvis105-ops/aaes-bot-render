import os
import json
import random
from datetime import datetime
from streaks import days_inactive

PATH = "data/comeback_messages.json"


# ----------------------------------------------------
# Default motivational messages
# ----------------------------------------------------
DEFAULT_MESSAGES = [
    "Your progress matters. Check in and continue your streak.",
    "A quick study session today helps you stay ahead.",
    "Learning builds up fast when you stay consistent.",
    "You are doing well. A small effort today makes a difference.",
    "Your goals are closer than you think. Keep going.",
    "Every day counts. Open the bot and try a question.",
    "Your streak wants you back. Continue your flow today.",
    "Small steps daily help you understand the course better.",
    "Take a moment to learn something today.",
    "Your future self benefits from every study moment."
]


# ----------------------------------------------------
# Ensure storage exists
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump(DEFAULT_MESSAGES, f, indent=4)


# ----------------------------------------------------
# Load all messages
# ----------------------------------------------------
def load_messages():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


# ----------------------------------------------------
# Add new motivational line (for admins)
# ----------------------------------------------------
def add_message(text):
    msgs = load_messages()
    msgs.append(text)
    with open(PATH, "w") as f:
        json.dump(msgs, f, indent=4)


# ----------------------------------------------------
# Get random message
# ----------------------------------------------------
def pick_random_message():
    msgs = load_messages()
    return random.choice(msgs)


# ----------------------------------------------------
# Identify inactive users for comeback reminders
# ----------------------------------------------------
def who_needs_reminder(all_users):
    need = []
    for uid in all_users:
        inactive = days_inactive(uid)
        if inactive >= 2 and inactive < 15:
            need.append(uid)
    return need


# ----------------------------------------------------
# Prepare comeback text
# ----------------------------------------------------
def comeback_text():
    msg = pick_random_message()
    return msg
