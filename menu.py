from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# -------------------------------------------
# MAIN MENU
# -------------------------------------------

def main_menu():
    kb = [
        [InlineKeyboardButton("📚 Materials", callback_data="materials")],
        [InlineKeyboardButton("🤖 Ask AI", callback_data="ask_ai")],
        [InlineKeyboardButton("🧰 Toolkit", callback_data="toolkit")],
        [InlineKeyboardButton("📢 Announcements", callback_data="ann")],
        [InlineKeyboardButton("🆘 Help Desk", callback_data="helpdesk")],
        [InlineKeyboardButton("📊 My Activity", callback_data="myact")]
    ]
    return InlineKeyboardMarkup(kb)


# -------------------------------------------
# MATERIALS MENU
# -------------------------------------------

def materials_menu():
    kb = [
        [InlineKeyboardButton("📖 Slides", callback_data="slides")],
        [InlineKeyboardButton("📑 Past Questions", callback_data="pastq")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(kb)


# -------------------------------------------
# TOOLKIT MENU
# -------------------------------------------

def toolkit_menu():
    kb = [
        [InlineKeyboardButton("📘 Build a Skill", callback_data="skills")],
        [InlineKeyboardButton("📏 GPA Calculator", callback_data="gpa")],
        [InlineKeyboardButton("🗓 Academic Calendar", callback_data="calendar")],
        [InlineKeyboardButton("🧮 Unit Converter", callback_data="converter")],
        [InlineKeyboardButton("🔧 Engineering Formulas", callback_data="formulas")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(kb)


# -------------------------------------------
# ANNOUNCEMENTS MENU
# -------------------------------------------

def announcements_menu():
    kb = [
        [InlineKeyboardButton("📢 View Announcements", callback_data="ann_view")],
        [InlineKeyboardButton("✈️ Daily Flight Log", callback_data="flightlog")],
        [InlineKeyboardButton("💼 Internship Alerts", callback_data="internship")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(kb)


# -------------------------------------------
# SKILL MENU (DYNAMIC)
# -------------------------------------------

def skill_menu(skills):
    kb = []
    for s in skills:
        kb.append([InlineKeyboardButton(s, callback_data=f"skill_{s}")])

    kb.append([InlineKeyboardButton("⬅️ Back", callback_data="back_toolkit")])

    return InlineKeyboardMarkup(kb)


# -------------------------------------------
# HELP DESK MENU
# -------------------------------------------

def helpdesk_menu():
    kb = [
        [InlineKeyboardButton("📝 Report an Issue", callback_data="helpdesk_start")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(kb)


# -------------------------------------------
# BACK BUTTONS ONLY
# -------------------------------------------

def back_to_main():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
    )

def back_to_toolkit():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="back_toolkit")]]
    )
