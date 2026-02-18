import json
import os
from datetime import datetime

PATH = "data/announcements.json"


# ----------------------------------------------------
# Init store
# ----------------------------------------------------
def init_store():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump([], f)


# ----------------------------------------------------
# Load and save
# ----------------------------------------------------
def load_announcements():
    init_store()
    with open(PATH, "r") as f:
        return json.load(f)


def save_announcements(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------------------------------
# Add announcement
# ----------------------------------------------------
def add_announcement(text, tag="general", author="AAES Bot"):
    """
    Tags allowed:
    general
    internship
    flightlog
    exam
    urgent
    """
    data = load_announcements()

    new = {
        "author": author,
        "text": text,
        "tag": tag.lower(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    data.append(new)
    save_announcements(data)
    return True


# ----------------------------------------------------
# Delete announcement
# ----------------------------------------------------
def delete_announcement(index):
    data = load_announcements()
    if index < 0 or index >= len(data):
        return None

    removed = data.pop(index)
    save_announcements(data)
    return removed


# ----------------------------------------------------
# Format announcements for display
# ----------------------------------------------------
def format_announcements():
    data = load_announcements()

    if not data:
        return "No announcements yet."

    out = ""

    for i, a in enumerate(data):
        tag_icon = {
            "general": "📰",
            "internship": "💼",
            "urgent": "⚠️",
            "flightlog": "✈️",
            "exam": "📘"
        }.get(a["tag"], "📝")

        out += (
            f"{tag_icon}  {i + 1}. {a['text']}\n"
            f"By: {a['author']}\n"
            f"Time: {a['timestamp']}\n\n"
        )

    return out.strip()


# ----------------------------------------------------
# Return latest flight log
# ----------------------------------------------------
def get_latest_flightlog():
    data = load_announcements()
    logs = [a for a in data if a["tag"] == "flightlog"]

    if not logs:
        return None

    return logs[-1]

    from datetime import datetime

def format_announcements_pretty(limit=10):
    data = load_announcements()
    if not data:
        return "📭 No announcements yet."

    lines = []
    for a in data[-limit:][::-1]:          # newest first
        tag_icon = {
            "general": "📰",
            "internship": "💼",
            "urgent": "⚠️",
            "flightlog": "✈️",
            "exam": "📘"
        }.get(a["tag"], "📝")

        ts = datetime.strptime(a["timestamp"], "%Y-%m-%d %H:%M")
        ts_str = ts.strftime("%d %b %Y, %H:%M")

        lines.append(
            f"{tag_icon} *{a['text']}*\n"
            f"👤 {a['author']}  •  🕒 {ts_str}"
        )

    return "\n\n".join(lines)
