import os
import json
import random
from datetime import datetime
from streaks import days_inactive
from exam_mode import exam_mode_active

PATH = "data/flight_log.json"

# ----------------------------------------------------
# Initialise storage
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
# Load / Save
# ----------------------------------------------------
def load_log():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_log(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Default fact pool
# ----------------------------------------------------
DEFAULT_FACTS = [
    "✈️Airbus A380 wings are so large that each one can hold 300 people standing.",
    "🌊Marine engineers design ships to survive waves over 15 meters high.",
    "🚗The fastest road car engine spins above 11,000 RPM.",
    "✈️Jet engines work by sucking in air, compressing it and igniting it.",
    "🚢Ships use bulbous bows to reduce drag and save fuel.",
    "🚗Most car engines lose 70 percent of their energy through heat and friction.",
    "✈️Helicopters can fly even if the engine fails using a trick called autorotation.",
    "🌊Modern submarines can stay underwater for months using nuclear power.",
    "✈️Turbochargers increase engine power by forcing more air into the cylinders.",
    "✈️A rocket engine works in space because it pushes exhaust backwards internally.",
    "✈️ A Boeing 747 has over 6 million parts.",
    "🚗 The average car has around 30,000 parts.",
    "🚢 The largest container ship can carry 24,000 TEU.",
    "🛰️ Satellites in LEO orbit Earth every 90 minutes.",
    "🚀 Rocket engines can reach temperatures of 3,300 °C.",
    "🧪 The SR-71 Blackbirds fuel was so special it had to be warmed before use.",
    "⚙️ A turbofan engine can have 40,000 individual blades.",
    "🛩️ The Airbus A380 has 22 wheels in its landing gear.",
    "🌊 The deepest submarine dive reached 10,928 m in the Mariana Trench.",
    "🧊 Aircraft wings are designed to flex up to 5 m during flight."
    "🌊 The Titanic was the largest ship of its time, measuring 882 feet long.",
    "🚗 The first practical automobile was built by Karl Benz in 1885.",
    "✈️ The Wright brothers made the first controlled, powered, and sustained heavier-than-air human flight in 1903.",
    "🌊 The Queen Mary 2 is one of the largest ocean liners ever built.",
    "🚗 The Bugatti Veyron can reach speeds of over 250 mph.",
    "✈️ The Concorde was the first supersonic passenger-carrying commercial airplane.",
    "🌊 The USS Enterprise was the world's first nuclear-powered aircraft carrier.",
    "🚗 The Tesla Model S is one of the first mass-produced electric vehicles.",
    "✈️ The Space Shuttle was the first reusable spacecraft.",
    "🌊 The Great Eastern was the largest ship in the world when it was launched in 1858.",
    "🚗 The first Formula 1 World Championship was held in 1950.",
    "✈️ The Boeing 787 Dreamliner is made of 50% composite materials.",
    "🌊 The RMS Lusitania was sunk by a German U-boat in 1915.",
    "🚗 The first mass-produced hybrid car was the Toyota Prius.",
    "✈️ The Lockheed SR-71 Blackbird is the fastest air-breathing manned aircraft.",
    "🌊 The SS United States holds the record for the fastest transatlantic crossing.",
    "🚗 The first self-driving car was demonstrated in 1984.",
    "✈️ The Airbus A350 XWB has a wingspan of over 212 feet.",
    "🌊 The HMS Victory is the oldest commissioned warship in the world.",
    "🚗 The first car to reach 100 mph was the Mercedes-Benz T80.",
    "✈️ The Bell X-1 was the first aircraft to break the sound barrier.",
    "🌊 The SS Great Britain was the first iron-hulled, propeller-driven ship to cross the Atlantic.",
    "🚗 The first production car with a V8 engine was the Cadillac V-8.",
    "✈️ The F-22 Raptor is one of the most advanced fighter jets in the world.",
    "🌊 The SS Normandie was the first ship to have a stabilizer system.",
    "🚗 The first car with airbags was the Oldsmobile Toronado.",
    "✈️ The Boeing 747 was the first wide-body commercial aircraft.",
    "🌊 The USS Missouri is one of the most famous battleships in history.",
    "🚗 The first car with anti-lock brakes was the Mercedes-Benz S-Class.",
    "✈️ The Lockheed U-2 is a high-altitude reconnaissance aircraft.",
    "🌊 The RMS Queen Mary was one of the fastest ocean liners.",
    "🚗 The first car with GPS navigation was the Oldsmobile 88.",
    "✈️ The Boeing 737 is one of the most produced commercial aircraft.",
    "🌊 The SS United States was designed by naval architect William Francis Gibbs.",
    "🚗 The first car with air conditioning was the Packard 180.",
    "✈️ The F-35 Lightning II is a multirole fighter aircraft.",

]

# ----------------------------------------------------
# Encoding and Decoding Functions
# ----------------------------------------------------

# Define placeholders for special characters and emojis
# daily_flight_log.py

PLACEHOLDERS = {
    "✈️": "FLY",
    "🚗": "CAR",
    "🚢": "SHIP",
    "🛰️": "SATELLITE",
    "🚀": "ROCKET",
    "🧪": "LAB",
    "⚙️": "GEAR",
    "🛩️": "PLANE",
    "🌊": "WAVE",
    "🧊": "ICE",
    "\n": "__NL__",
    " ": "_"
}

REVERSE_PLACEHOLDERS = {v: k for k, v in PLACEHOLDERS.items()}

def encode_fact(fact):
    for original, placeholder in PLACEHOLDERS.items():
        fact = fact.replace(original, placeholder)
    return fact

def decode_fact(encoded_fact):
    for placeholder, original in REVERSE_PLACEHOLDERS.items():
        encoded_fact = encoded_fact.replace(placeholder, original)
    return encoded_fact

# Encode all facts
ENCODED_FACTS = [encode_fact(fact) for fact in DEFAULT_FACTS]

# Ensure each encoded fact is within the 64-byte limit
ENCODED_FACTS = [fact[:64] for fact in ENCODED_FACTS]

# ----------------------------------------------------
# Get daily fact
# ----------------------------------------------------
def get_daily_fact():
    data = load_log()
    facts = data.get("facts", [])

    if not facts:
        facts = DEFAULT_FACTS

    fact = random.choice(facts)
    return f"✈️ *Did you know...*\n\n*{fact}*\n\n*Follow for more!*"

# ----------------------------------------------------
# Add a new fact
# ----------------------------------------------------
def add_fact(fact):
    data = load_log()

    if "facts" not in data:
        data["facts"] = []

    data["facts"].append(fact)
    save_log(data)
    return True

# ----------------------------------------------------
# Check if today's fact was already sent
# ----------------------------------------------------
def should_send_fact():
    return True

def mark_fact_sent():
    data = load_log()
    data["last_sent"] = str(datetime.now().date())
    save_log(data)

# ----------------------------------------------------
# Comeback reminders based on inactivity
# ----------------------------------------------------
def get_comeback_message(user_id):
    d = days_inactive(user_id)

    if d >= 10:
        return "Your engines have been quiet for a while. Come back and learn something new."
    if d >= 5:
        return "Your streak awaits. Tap the bot and continue learning."
    if d >= 3:
        return "You are close to losing your streak. Ask one question to keep it alive."

    return None

# ----------------------------------------------------
# Send daily flight log
# ----------------------------------------------------

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_daily_flight_log(app):
    logger.info("Daily flight log job triggered")
    if not should_send_fact():
        logger.info("Daily flight log is disabled today")
        return

    fact = get_daily_fact()
    logger.info(f"Fact to be sent: {fact}")
    subscribers = list_subscribers()
    logger.info(f"Sending daily flight log to {len(subscribers)} subscribers")

    for uid in subscribers:
        try:
            encoded_fact = encode_fact(fact)
            keyboard = [
                [InlineKeyboardButton("Want to know more?", callback_data=f"fact_more:{encoded_fact}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await app.bot.send_message(
                int(uid),
                fact,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            logger.info(f"Sent daily flight log to {uid}")
        except Exception as e:
            logger.warning(f"Failed to send daily fact to {uid}: {e}")

    mark_fact_sent()