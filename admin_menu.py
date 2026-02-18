from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_panel_markup():
    kb = [
        [InlineKeyboardButton("📢 Send Announcement", callback_data="admin_announce")],
        [InlineKeyboardButton("💼 Post Internship Alert", callback_data="admin_internship")],
        [InlineKeyboardButton("✈️ Add Daily Fact", callback_data="admin_fact")],
        [InlineKeyboardButton("👤 Add Admin", callback_data="admin_add")],
        [InlineKeyboardButton("🗑 Remove Admin", callback_data="admin_remove")],
        [InlineKeyboardButton("📊 Subscribers", callback_data="admin_subs")],
        [InlineKeyboardButton("Back ◀️", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(kb)