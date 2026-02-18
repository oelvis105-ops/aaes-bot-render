import os
import json
from datetime import datetime
from streaks import load_streaks

PATH = "data/leaderboard.json"


# -----------------------------------------
# Ensure file exists
# -----------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump({}, f, indent=4)


# -----------------------------------------
# Save leaderboard snapshot (optional)
# -----------------------------------------
def save_snapshot(data):
    _init()
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)


# -----------------------------------------
# Load stored leaderboard
# -----------------------------------------
def load_snapshot():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


# -----------------------------------------
# Build leaderboard from streak data
# -----------------------------------------
def build_leaderboard():
    streaks = load_streaks()

    ranking = []

    for uid, data in streaks.items():
        streak = data.get("streak", 0)
        name = data.get("name", "Student")

        ranking.append({
            "id": uid,
            "name": name,
            "streak": streak
        })

    ranking.sort(key=lambda x: x["streak"], reverse=True)

    return ranking


# -----------------------------------------
# Top 10 only
# -----------------------------------------
def top_ten():
    board = build_leaderboard()
    return board[:10]


# -----------------------------------------
# Format leaderboard text for Telegram
# -----------------------------------------
def format_leaderboard():
    board = top_ten()

    if len(board) == 0:
        return "Leaderboard is empty."

    out = "Top Streaks\n\n"
    rank = 1

    for entry in board:
        out += f"{rank}. {entry['name']}  Streak: {entry['streak']}\n"
        rank += 1

    return out
