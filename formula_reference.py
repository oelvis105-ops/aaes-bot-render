import os
import json

PATH = "data/formulas.json"


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
def load_formulas():
    _init()
    with open(PATH, "r") as f:
        return json.load(f)


def save_formulas(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)

FORMULAS = [
    "Lift Force = 1/2 * ρ * V^2 * S * CL"
]

# ----------------------------------------------------
# Add a formula to a category
# ----------------------------------------------------
def add_formula(category, name, expression, explanation=""):
    data = load_formulas()

    if category not in data:
        data[category] = []

    entry = {
        "name": name,
        "expression": expression,
        "explanation": explanation
    }

    data[category].append(entry)
    save_formulas(data)
    return True


# ----------------------------------------------------
# Remove formula by index
# ----------------------------------------------------
def remove_formula(category, index):
    data = load_formulas()

    if category not in data:
        return False
    if index < 0 or index >= len(data[category]):
        return False

    removed = data[category].pop(index)
    save_formulas(data)
    return removed


# ----------------------------------------------------
# Get all formulas under a category
# ----------------------------------------------------
def get_formulas(category):
    data = load_formulas()
    return data.get(category, [])


# ----------------------------------------------------
# Format output for Telegram
# ----------------------------------------------------
def format_formula_list(category):
    data = load_formulas()

    if category not in data or len(data[category]) == 0:
        return "No formulas saved under this category yet."

    out = f"{category} Formulas\n\n"

    for i, f in enumerate(data[category]):
        out += f"{i+1}. {f['name']}\n"
        out += f"   Formula: {f['expression']}\n"
        if f["explanation"]:
            out += f"   Note: {f['explanation']}\n"
        out += "\n"

    return out


# ----------------------------------------------------
# List categories
# ----------------------------------------------------
def list_formula_categories():
    data = load_formulas()
    return list(data.keys())

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def category_buttons():
    """Return InlineKeyboardMarkup with all categories."""
    cats = list_formula_categories()
    kb = [[InlineKeyboardButton(c, callback_data=f"formcat_{c}")] for c in cats]
    kb.append([InlineKeyboardButton("Back ◀️", callback_data="toolkit")])
    return InlineKeyboardMarkup(kb)

def formula_detail_buttons(category, idx):
    formulas = get_formulas(category)
    kb = []
    if idx > 0:
        kb.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"formnav_{category}_{idx-1}"))
    if idx < len(formulas) - 1:
        kb.append(InlineKeyboardButton("Next ➡️", callback_data=f"formnav_{category}_{idx+1}"))
    kb.append(InlineKeyboardButton("Back to list", callback_data="toolkit_formulas"))
    return InlineKeyboardMarkup([kb])
