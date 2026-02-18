import os
import json
from google_drive import search_drive

PATH = "data/timetable.json"


# ----------------------------------------------------
# Initialize storage
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
def load_timetable():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_timetable(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Admin sets timetable for a particular class
# ----------------------------------------------------
def set_class_timetable(level, program, content):
    """
    level: 100, 200, 300, 400
    program: AUTO, AERO, MARINE
    content: text describing timetable or Drive link
    """

    level = str(level)
    program = program.upper()

    data = load_timetable()

    if level not in data:
        data[level] = {}

    data[level][program] = content
    save_timetable(data)
    return True


# ----------------------------------------------------
# Get timetable for class
# ----------------------------------------------------
def get_class_timetable(level, program):
    level = str(level)
    program = program.upper()

    data = load_timetable()

    if level not in data:
        return "No timetable stored for this level."

    if program not in data[level]:
        return "No timetable stored for this class."

    return data[level][program]


# ----------------------------------------------------
# Fetch the most recent AAES-wide academic calendar
# from Google Drive
# ----------------------------------------------------
def get_academic_calendar():
    """
    Searches AAES Drive for newest file containing 
    the keyword 'calendar'.
    """

    result = search_drive("calendar")

    if "No matching slide" in result:
        return "No academic calendar found."

    return result


# ----------------------------------------------------
# Get personal exam timetable link (set by admins)
# ----------------------------------------------------
def get_personal_exam_link():
    """
    Admins manually set this link below.
    """
    personal_link_path = "data/personal_exam_link.txt"

    if not os.path.exists(personal_link_path):
        return "Personal timetable link not set yet."

    with open(personal_link_path, "r") as f:
        return f.read().strip()


def set_personal_exam_link(link):
    personal_link_path = "data/personal_exam_link.txt"

    with open(personal_link_path, "w") as f:
        f.write(link)

    return True
