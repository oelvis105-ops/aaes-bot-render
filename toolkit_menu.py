from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def toolkit_menu():
    kb = [
        [InlineKeyboardButton("GPA Calculator", callback_data="tool_gpa")],
        [InlineKeyboardButton("Study Timetable Generator", callback_data="tool_timetable")],
        [InlineKeyboardButton("Engineering Formulas", callback_data="tool_formulas")],
        [InlineKeyboardButton("Unit Converter", callback_data="tool_units")],
        [InlineKeyboardButton("Scientific Constants", callback_data="tool_constants")],
        [InlineKeyboardButton("Build a Skill", callback_data="skills")]
        ]
    return InlineKeyboardMarkup(kb)

def toolkit_entry_message():
    return "Select a tool."
def academic_calendar_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 View Academic Calendar", callback_data="show_calendar")],
        [InlineKeyboardButton("Back ◀️", callback_data="toolkit")]
    ])