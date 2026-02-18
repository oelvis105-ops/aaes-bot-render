import os
import json
import random
from datetime import datetime
from streaks import days_inactive, update_streak

PATH = "data/daily_facts.json"


# ----------------------------------------------------
# Initialize storage
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({
                "facts": [],
                "last_sent": ""
            }, f)


# ----------------------------------------------------
# Load and Save
# ----------------------------------------------------
def load_facts():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_facts(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Default Facts (Used if database empty)
# ----------------------------------------------------
DEFAULT_FACTS = [
    "A jet engine sucks in more than 1,200 kg of air every minute during takeoff.",
    "Marine propellers can reach efficiencies of about 70 percent when optimally designed.",
    "Modern car airbags inflate in less than 40 milliseconds.",
    "The SR-71 Blackbird expands by several centimeters in flight due to extreme heat.",
    "CAT engines in large ships burn over 100 tons of fuel per day.",
    "A Formula One car can accelerate from 0 to 100 km/h in under 2.6 seconds.",
    "The Boeing 787 uses composite materials for over 50 percent of its structure.",
    "Submarines adjust their depth by controlling buoyancy in ballast tanks.",
    "Turbochargers recycle exhaust gases to boost engine power.",
    "Airbus A380 wings are flexible enough to bend over 7 meters upward."
]


# ----------------------------------------------------
# Get random fact
# ----------------------------------------------------
def get_daily_fact():
    data = load_facts()
    facts = data.get("facts", [])

    if not facts:
        facts = DEFAULT_FACTS

    return random.choice(facts)


# ----------------------------------------------------
# Add a new fact (admins)
# ----------------------------------------------------
def add_fact(text):
    data = load_facts()

    if "facts" not in data:
        data["facts"] = []

    data["facts"].append(text)
    save_facts(data)
    return True


# ----------------------------------------------------
# AI / Duolingo-style comeback messages
# ----------------------------------------------------
COMEBACK_MESSAGES = [
    "Your engines are cooling down. Come back and learn something today.",
    "AAES needs your brain power. Jump back in.",
    "Your streak is calling. Continue where you left off.",
    "Every small session counts toward your engineering journey.",
    "Fuel your mind. You are one fact away from progress."
]


def get_comeback_message():
    return random.choice(COMEBACK_MESSAGES)


# ----------------------------------------------------
# Should we send comeback message?
# ----------------------------------------------------
def check_comeback(user_id):
    inactivity_days = days_inactive(user_id)

    if inactivity_days >= 3:
        return get_comeback_message()

    return None


# ----------------------------------------------------
# Update streak when user interacts
# ----------------------------------------------------
def register_interaction(user_id):
    return update_streak(user_id)


# ----------------------------------------------------
# Daily Scheduler Support
# ----------------------------------------------------
def should_send_today():
    """
    Prevents duplicate sending on the same day.
    """
    data = load_facts()
    last = data.get("last_sent", "")
    today = str(datetime.now().date())

    return today != last


def mark_sent_today():
    data = load_facts()
    data["last_sent"] = str(datetime.now().date())
    save_facts(data)
