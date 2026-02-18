import json
import os

PATH = "data/course_credits.json"


# ----------------------------------------------------
# Initialise storage
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({}, f, indent=4)


# ----------------------------------------------------
# Load / Save
# ----------------------------------------------------
def load_credits():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_credits(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Add course credit value (admin only)
# ----------------------------------------------------
def add_course_credit(course_code, credit):
    data = load_credits()
    data[course_code.upper()] = credit
    save_credits(data)
    return True


# ----------------------------------------------------
# Get credit for one course
# ----------------------------------------------------
def get_course_credit(course_code):
    data = load_credits()
    return data.get(course_code.upper(), None)


# ----------------------------------------------------
# Calculate total credits (student inputs multiple)
# ----------------------------------------------------
def calculate_total_credits(course_list):
    """
    course_list example:
    ["AE 101", "ME 203", "MA 271"]

    Returns:
    (total_credits, missing_courses)
    """
    data = load_credits()

    total = 0
    missing = []

    for code in course_list:
        key = code.upper()
        if key in data:
            total += data[key]
        else:
            missing.append(key)

    return total, missing
