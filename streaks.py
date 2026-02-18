import os
import json
from datetime import datetime, timedelta

PATH = "data/streaks.json"


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
# Load and save
# ----------------------------------------------------
def load_streaks():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_streaks(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Update streak when user interacts
# ----------------------------------------------------
def update_streak(user_id):
    user_id = str(user_id)
    data = load_streaks()

    today = datetime.now().date()

    if user_id not in data:
        data[user_id] = {
            "streak": 1,
            "last_active": str(today)
        }
        save_streaks(data)
        return 1

    last_active = datetime.fromisoformat(data[user_id]["last_active"]).date()

    if last_active == today:
        # Already counted today
        return data[user_id]["streak"]

    if last_active == today - timedelta(days=1):
        # Continue streak
        data[user_id]["streak"] += 1
    else:
        # Streak broken
        data[user_id]["streak"] = 1

    data[user_id]["last_active"] = str(today)
    save_streaks(data)

    return data[user_id]["streak"]


# ----------------------------------------------------
# Get current streak
# ----------------------------------------------------
def get_streak(user_id):
    data = load_streaks()
    user_id = str(user_id)

    if user_id not in data:
        return 0

    return data[user_id]["streak"]


# ----------------------------------------------------
# Detect inactivity for comeback messages
# ----------------------------------------------------
def days_inactive(user_id):
    data = load_streaks()
    user_id = str(user_id)

    if user_id not in data:
        return 999  # treat as long inactive

    last_active = datetime.fromisoformat(data[user_id]["last_active"]).date()
    today = datetime.now().date()

    return (today - last_active).days
