import os
import json
from datetime import datetime

PATH = "data/helpdesk.json"

# ----------------------------------------------------
# Ensure file exists
# ----------------------------------------------------
def _init():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

# ----------------------------------------------------
# Load / Save
# ----------------------------------------------------
def load_tickets():
    _init()
    with open(PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tickets(data):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ----------------------------------------------------
# Add a new ticket
# ----------------------------------------------------
def add_ticket(uid, name, text):
    tickets = load_tickets()
    tickets.append({
        "user_id": uid,
        "name": name,
        "text": text,
        "status": "pending",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_tickets(tickets)
    return True

# ----------------------------------------------------
# Mark ticket resolved
# ----------------------------------------------------
def resolve_ticket(index):
    tickets = load_tickets()
    if index < 0 or index >= len(tickets):
        return None
    tickets[index]["status"] = "resolved"
    save_tickets(tickets)
    return tickets[index]

# ----------------------------------------------------
# Format tickets for admin panel (with buttons)
# ----------------------------------------------------
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def format_tickets_with_buttons(limit=10):
    tickets = load_tickets()
    if not tickets:
        return "📭 No tickets yet.", InlineKeyboardMarkup([])

    lines = []
    kb = []

    # newest first
    for rev_idx, t in enumerate(reversed(tickets[-limit:])):
        real_index = len(tickets) - 1 - rev_idx
        lines.append(
            f"👤 {t['name']}  (ID: {t['user_id']})\n"
            f"📝 {t['text']}\n"
            f"🕒 {t['timestamp']}  |  Status: {t['status']}"
        )
        if t["status"] == "pending":
            kb.append([InlineKeyboardButton(
                f"✅ Mark Resolved #{real_index}",
                callback_data=f"resolve_ticket_{real_index}"
            )])

    kb.append([InlineKeyboardButton("Back ◀️", callback_data="admin_tickets")])
    return "\n\n".join(lines), InlineKeyboardMarkup(kb)

# ---------- public helpers ----------
__all__ = ["add_ticket", "resolve_ticket", "format_tickets_with_buttons"]