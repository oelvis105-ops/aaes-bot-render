import json
import os

ADMIN_PATH = "data/admins.json"


# -------------------------------------------
# Ensure admin file exists
# -------------------------------------------

def init_admin_file():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(ADMIN_PATH):
        with open(ADMIN_PATH, "w") as f:
            json.dump([], f)


# -------------------------------------------
# Load admins
# -------------------------------------------

def load_admins():
    init_admin_file()
    with open(ADMIN_PATH, "r") as f:
        return json.load(f)


# -------------------------------------------
# Save admins
# -------------------------------------------

def save_admins(admins):
    with open(ADMIN_PATH, "w") as f:
        json.dump(admins, f, indent=4)


# -------------------------------------------
# Check if a user is admin
# -------------------------------------------

def is_admin(user_id):
    admins = load_admins()
    return str(user_id) in admins


# -------------------------------------------
# Add admin
# -------------------------------------------

def add_admin(user_id):
    admins = load_admins()

    if str(user_id) in admins:
        return False

    admins.append(str(user_id))
    save_admins(admins)
    return True


# -------------------------------------------
# Remove admin
# -------------------------------------------

def remove_admin(user_id):
    admins = load_admins()

    if str(user_id) not in admins:
        return False

    admins.remove(str(user_id))
    save_admins(admins)
    return True
