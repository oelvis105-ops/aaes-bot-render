import os
import json
from difflib import get_close_matches

PATH = "data/calendar.json"

# ------------------------------------------------------------------
# Initialise storage
# ------------------------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({
                "latest_calendar_link": "",
                "knust_personal_timetable_link": "",
                "class_timetables": {},
            }, f, indent=4)


def load_calendar():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_calendar(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ------------------------------------------------------------------
# Save general AAES calendar link (from Google Drive)
# ------------------------------------------------------------------
def update_latest_calendar(link):
    data = load_calendar()
    data["latest_calendar_link"] = link
    save_calendar(data)


# ------------------------------------------------------------------
# Save personal KNUST timetable link
# ------------------------------------------------------------------
def update_personal_timetable(link):
    data = load_calendar()
    data["knust_personal_timetable_link"] = link
    save_calendar(data)


# ------------------------------------------------------------------
# Store timetable for each class (12 classes)
# Example: update_class_timetable("Aero L200", link)
# ------------------------------------------------------------------
def update_class_timetable(class_name, link):
    data = load_calendar()
    data["class_timetables"][class_name] = link
    save_calendar(data)


# ------------------------------------------------------------------
# Retrieve class timetable with fuzzy matching
# ------------------------------------------------------------------
def get_class_timetable(query):
    data = load_calendar()
    classes = list(data["class_timetables"].keys())

    if len(classes) == 0:
        return "No class timetables uploaded yet."

    match = get_close_matches(query, classes, n=1, cutoff=0.4)
    if not match:
        return "No matching class found."

    return data["class_timetables"][match[0]]


# ------------------------------------------------------------------
# Fetch all calendar-related links
# ------------------------------------------------------------------
def get_calendar_bundle():
    data = load_calendar()

    msg = "Calendar Resources\n\n"

    if data["latest_calendar_link"]:
        msg += f"AAES Academic Calendar: {data['latest_calendar_link']}\n\n"
    else:
        msg += "AAES Academic Calendar: Not added yet.\n\n"

    if data["knust_personal_timetable_link"]:
        msg += f"KNUST Personal Exam Timetable: {data['knust_personal_timetable_link']}\n\n"
    else:
        msg += "KNUST Personal Exam Timetable: Not added yet.\n\n"

    if len(data["class_timetables"]) > 0:
        msg += "Class Timetables:\n"
        for cls, link in data["class_timetables"].items():
            msg += f"- {cls}: {link}\n"
    else:
        msg += "No class timetables uploaded yet."

    return msg
