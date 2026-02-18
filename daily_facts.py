import os
import json
import random

FACT_PATH = "data/daily_facts.json"
COMEBACK_PATH = "data/comeback_messages.json"


# ------------------------------------------------------
# Initialise storage if missing
# ------------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(FACT_PATH):
        default_facts = [
            "The first aircraft to exceed the speed of sound was the Bell X-1 in 1947.",
            "Modern jet engines operate at temperatures higher than the melting point of their materials.",
            "A ship’s propeller is intentionally asymmetrical for better hydrodynamic efficiency.",
            "Some car engines use variable valve timing to improve both power and fuel efficiency.",
            "Marine engineers design hull shapes based on fluid-dynamics equations similar to those used in aerospace.",
            "Aircraft wings generate lift because of pressure differences explained by Bernoulli's principle.",
            "Electric vehicles convert over 85 percent of their battery energy into motion.",
            "The F1 car engine can reach up to 15,000 RPM during races.",
            "The Boeing 747 contains about six million individual parts.",
            "Submarines use ballast tanks to control buoyancy and depth.",
            "The Apollo Guidance Computer had less processing power than today’s basic calculators.",
            "Aeroelasticity studies how wings bend and twist under aerodynamic loads.",
            "Composite materials in aircraft reduce weight while keeping strength high.",
            "Anti-lock braking systems help prevent skidding by rapidly pulsing the brakes.",
            "Marine diesel engines can exceed heights of 15 meters in container ships."
        ]
        with open(FACT_PATH, "w") as f:
            json.dump(default_facts, f, indent=4)

    if not os.path.exists(COMEBACK_PATH):
        comeback = [
            "Your cockpit misses you. One quick lesson today?",
            "Engines are warm, your streak wants to take off again.",
            "Small study today strengthens your engineering tomorrow.",
            "Time for a quick check. You learn something small, you grow a lot.",
            "AAES never sleeps. Come back for a new fact.",
            "Your streak is waiting for ignition.",
            "The next lesson is lighter than a wing panel. Tap to continue.",
            "Real engineers train daily. Join the flight again."
        ]
        with open(COMEBACK_PATH, "w") as f:
            json.dump(comeback, f, indent=4)


# ------------------------------------------------------
# Loaders
# ------------------------------------------------------
def load_facts():
    _init()
    with open(FACT_PATH, "r") as f:
        return json.load(f)


def load_comeback_messages():
    _init()
    with open(COMEBACK_PATH, "r") as f:
        return json.load(f)


# ------------------------------------------------------
# Random selectors
# ------------------------------------------------------
def get_random_fact():
    facts = load_facts()
    if not facts:
        return "Engineering makes the world move."
    return random.choice(facts)


def get_random_comeback():
    msgs = load_comeback_messages()
    if not msgs:
        return "Return for your next lesson."
    return random.choice(msgs)


# ------------------------------------------------------
# Add new facts (admin use later)
# ------------------------------------------------------
def add_fact(text):
    facts = load_facts()
    if text not in facts:
        facts.append(text)
        with open(FACT_PATH, "w") as f:
            json.dump(facts, f, indent=4)
        return True
    return False
