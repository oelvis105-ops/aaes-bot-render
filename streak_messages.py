import random
from streaks import get_streak, days_inactive

# ----------------------------------------------------
# Streak celebration messages
# ----------------------------------------------------
def streak_message(user_id):
    streak = get_streak(user_id)

    if streak <= 1:
        return None

    messages = [
        f"Nice. You are on a {streak} day streak.",
        f"You studied for {streak} days straight. Keep going.",
        f"{streak} day streak logged.",
        f"{streak} days active. Good consistency."
    ]

    return random.choice(messages)


# ----------------------------------------------------
# Comeback messages for inactive users
# ----------------------------------------------------
def comeback_message(user_id):
    idle = days_inactive(user_id)

    if idle < 2:
        return None

    messages = [
        "You were gone for a while. Continue your progress.",
        "Welcome back. Check your saved courses.",
        "You are back. Pick one topic and start now.",
        "Good to see you again. Resume your study plan."
    ]

    return random.choice(messages)


# ----------------------------------------------------
# Motivational nudges
# ----------------------------------------------------
def nudge_message():
    nudges = [
        "Study for five minutes today.",
        "Pick one topic and review it.",
        "Complete one past question set.",
        "Open one slide and skim through.",
        "Small effort today helps your grades."
    ]
    return random.choice(nudges)
