import os
import json

PATH = "data/gpa.json"


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
def load_gpa():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_gpa(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Convert raw score to KNUST grade point
# ----------------------------------------------------
def score_to_point(score):
    score = float(score)

    if score >= 70:
        return 4        # A
    if score >= 60:
        return 3        # B
    if score >= 50:
        return 2        # C
    if score >= 40:
        return 1        # D
    return 0            # F


# ----------------------------------------------------
# Calculate semester GPA/CWA
# ----------------------------------------------------
def calculate_gpa(courses):
    total_credits = 0
    total_weighted = 0

    for course in courses:
        score = course["score"]
        credit = course["credit"]

        point = score_to_point(score)
        total_weighted += point * credit
        total_credits += credit

    if total_credits == 0:
        return 0

    gpa = total_weighted / total_credits
    return round(gpa, 2)


# ----------------------------------------------------
# Save last calculation for user
# ----------------------------------------------------
def save_user_gpa(user_id, courses):
    data = load_gpa()
    uid = str(user_id)

    gpa = calculate_gpa(courses)

    data[uid] = {
        "courses": courses,
        "gpa": gpa
    }

    save_gpa(data)
    return gpa


# ----------------------------------------------------
# Get previous calculation
# ----------------------------------------------------
def get_user_gpa(user_id):
    data = load_gpa()
    return data.get(str(user_id), None)
