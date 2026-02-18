import random
from datetime import datetime
from streaks import update_streak
from streak_messages import streak_message, comeback_message, nudge_message


# ----------------------------------------------------
# Startup message shown when user presses /start
# ----------------------------------------------------
def startup_message(user_id, name):
    # Update streak and detect activity
    streak = update_streak(user_id)

    # Dynamic lines
    base = f"Welcome {name}. Select an option."
    streak_msg = streak_message(user_id)
    comeback_msg = comeback_message(user_id)

    parts = [base]

    if comeback_msg:
        parts.append(comeback_msg)
    if streak_msg:
        parts.append(streak_msg)

    return "\n".join(parts)


# ----------------------------------------------------
# Messages sent when user goes inactive for long
# ----------------------------------------------------
def long_inactive_notification(user_id):
    idle_days = datetime.now().weekday()

    # Simple rule: send a nudge every few idle days
    if idle_days % 3 == 0:
        return nudge_message()

    return None


# ----------------------------------------------------
# Optional daily nudges
# ----------------------------------------------------
def morning_nudge():
    lines = [
        "Start with a short study session.",
        "Review one slide today.",
        "Check past questions for your next course.",
        "Open the toolkit and use one tool.",
        "Make progress today."
    ]
    return random.choice(lines)
