# bot.py  –  AAES Study Bot (folder-first search, 1.9 GB files, persistent menu)
import asyncio
from multiprocessing import context
import os
import logging
from docx import Document
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    CallbackContext,
    ContextTypes,
)
from flask import Flask, request
from telegram import Bot
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io
import mimetypes
from telegram.constants import ParseMode
import warnings
from google.auth import _helpers

# Suppress the file_cache warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google.auth")
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, InputFile, InputMediaPhoto
import random
from utils import read_file_content, display_exec_info, list_files_in_folder
from admin import is_admin, load_admins, add_admin, remove_admin
from admin_menu import admin_panel_markup
from formula_reference import add_formula
add_formula("Aerodynamics", "Lift Force", "L = ½ ρ V² S CL", "Works for subsonic flight")
add_formula("Thermodynamics", "Ideal Gas Law", "PV = nRT")
# local modules
from utils import ai_chat_response, handle_upload, send_drive_file, add_turn, build_prompt
from drive_search import search_drive, _find_folder_id, _files_in_folder
from activity import log_activity, get_user_activity
from announcements import add_announcement, load_announcements
from helpdesk import add_ticket
from skill_manager_v2 import (
    available_skills,
    skill_label,
    lesson_button_list,
    get_lesson_by_number,
    skill_lesson_count,
)
from skill_progress import get_last_lesson, set_last_lesson
from profiles import get_profile, update_profile
from notify import subscribe, unsubscribe, list_subscribers
from streaks import update_streak
from gpa_engine import calculate_gpa
from skill_engine import (
    fetch_skill_intro, list_skills, get_lessons, get_progress, set_progress,
    get_quiz, save_quiz, clear_progress
)
from daily_flight_log import encode_fact, decode_fact

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # <-- changed import
from daily_flight_log import get_daily_fact, should_send_fact, mark_fact_sent
from exam_mode import exam_mode_active, exam_countdown
from utils import prettify_answer
from collections import deque
from state_db import get_state, set_state
# uid -> deque of {"role": "user"|"assistant", "text": str, "file": str|None}
CONVERSATION = {}
MAX_HISTORY = 10
# ---------- global vars ----------

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set in .env file")

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SA_PATH", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

ADMINS = load_admins() if "load_admins" in globals() else []
USER_STATE = {}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("aaes-bot")

# ---------- keyboards ----------
def persistent_menu(is_admin=False):
    """Reply keyboard that stays pinned at the bottom."""
    kb = [
        [KeyboardButton("📚 Materials"), KeyboardButton("💬 Ask AI")],
        [KeyboardButton("📣 Announcements"), KeyboardButton("🛠 Toolkit")],
        [KeyboardButton("🏛️ AAES Hub"), KeyboardButton("🆘 Help Desk")],
    ]
    if is_admin:
        kb.append([KeyboardButton("🛠 Admin Panel")])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=False)

#-----materials flow-----
def materials_menu_markup():
    """Level selector (first step of materials flow)."""
    kb = [
        [InlineKeyboardButton("Level 100", callback_data="level_100")],
        [InlineKeyboardButton("Level 200", callback_data="level_200")],
        [InlineKeyboardButton("Level 300", callback_data="level_300")],
        [InlineKeyboardButton("Level 400", callback_data="level_400")],
        [InlineKeyboardButton("Global Search 🔎", callback_data="materials_global")],
        [InlineKeyboardButton("Back ◀️", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(kb)

def materials_type_markup():
    """Slides vs Past Questions selector (second step of materials flow)."""
    kb = [
        [InlineKeyboardButton("Slides 📄", callback_data="materials_slides")],
        [InlineKeyboardButton("Past Questions 📝", callback_data="materials_pastq")],
        [InlineKeyboardButton("Back ◀️", callback_data="materials")],
    ]
    return InlineKeyboardMarkup(kb)

def not_found_markup(back="materials"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=back)]])

def toolkit_menu_markup():
    """Top Level Toolkit Menu."""
    kb = [
        [InlineKeyboardButton("GPA Calculator 📊", callback_data="toolkit_gpa")],
        [InlineKeyboardButton("Build a Skill ⚙️", callback_data="toolkit_skill")],
        [InlineKeyboardButton("Formulas 📘", callback_data="toolkit_formulas")],
        [InlineKeyboardButton("Back ◀️", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(kb)

def gpa_type_markup():
    """GPA sub-menu."""
    kb = [
        [InlineKeyboardButton("📘 Semester GPA", callback_data="gpa_semester")],
        [InlineKeyboardButton("📚 Cumulative GPA", callback_data="gpa_cumulative")],
        [InlineKeyboardButton("Back ◀️", callback_data="toolkit")],
    ]
    return InlineKeyboardMarkup(kb)

def skill_lessons_markup(skill: str, lesson_count: int, progress: int):
    """Keyboard for picking a lesson inside a skill."""
    kb = []
    for idx in range(lesson_count):
        label = f"Lesson {idx+1}"
        if idx <= progress:
            label += " ✅"
        kb.append([InlineKeyboardButton(label, callback_data=f"skilllesson_{skill}_{idx}")])
    if 0 <= progress < lesson_count - 1:
        kb.append([InlineKeyboardButton("▶️ Continue", callback_data=f"skilllesson_{skill}_{progress+1}")])
    kb.append([InlineKeyboardButton("Back ◀️", callback_data="toolkit_skill")])  # ← to skill list
    return InlineKeyboardMarkup(kb)

def hub_menu_markup():
    """AAES Hub Menu."""
    kb = [
        [InlineKeyboardButton("About AAES ℹ️", callback_data="hub_about")],
        [InlineKeyboardButton("Meet the Execs 👥", callback_data="hub_execs")],
        [InlineKeyboardButton("My Activity 📈", callback_data="hub_activity")],
        [InlineKeyboardButton("Back ◀️", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(kb)

def announcements_menu_markup():
    """Announcements Menu."""
    kb = [
        [InlineKeyboardButton("View Announcements 📣", callback_data="announcements")],
        [InlineKeyboardButton("Internship Alerts 💼", callback_data="internship_alerts")],
        [InlineKeyboardButton("Back ◀️", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(kb)

def admin_panel_markup():
    """Admin Panel Menu."""
    kb = [
        [InlineKeyboardButton("Make Announcement 📢", callback_data="admin_announce")],
        [InlineKeyboardButton("Post Internship Alert 💼", callback_data="admin_internship")],
        [InlineKeyboardButton("Add Daily Flight Log Fact ✈️", callback_data="admin_fact")],
        [InlineKeyboardButton("Add Admin ➕", callback_data="admin_add")],
        [InlineKeyboardButton("Remove Admin ➖", callback_data="admin_remove")],
        [InlineKeyboardButton("View Subscribers 📊", callback_data="admin_subs")],
        [InlineKeyboardButton("📘 Toggle Exam Mode", callback_data="admin_toggle_exam")],
        [InlineKeyboardButton("📋 View Help-Desk Tickets", callback_data="admin_tickets")],
        [InlineKeyboardButton("Back ◀️", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(kb)

def not_found_markup(back="menu"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=back)]])
# ---------- helpers ----------
async def route_persistent_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle the persistent reply-keyboard buttons."""
    text = (update.message.text or "").strip()
    uid = update.effective_user.id

    mapping = {
        "📚 Materials": "materials",
        "💬 Ask AI": "ask_ai",
        "📣 Announcements": "announcements",
        "🛠 Toolkit": "toolkit",
        "🏛️ AAES Hub": "hub",
        "🆘 Help Desk": "helpdesk",
    }

    # Add admin panel only if user is admin
    if is_admin(uid):
        mapping["🛠 Admin Panel"] = "admin"

    if text not in mapping:
        return False

    if mapping[text] == "materials":
        await update.message.reply_text("Choose level", reply_markup=materials_menu_markup())

    elif mapping[text] == "ask_ai":
        set_state(uid,"ask")
        await update.message.reply_text("Type your question or upload slides. Use /cancel to return.")

    elif mapping[text] == "announcements":
        data = load_announcements()
        if not data:
            await update.message.reply_text("No announcements yet.", reply_markup=persistent_menu(is_admin(uid)))
        else:
            from announcements import format_announcements_pretty
            text = format_announcements_pretty(10)
            await update.message.reply_text(text, parse_mode="Markdown", reply_markup=persistent_menu(is_admin(uid)))

    elif mapping[text] == "toolkit":
        await update.message.reply_text("Toolkit", reply_markup=toolkit_menu_markup())

    elif mapping[text] == "hub":
        await update.message.reply_text("AAES Hub", reply_markup=hub_menu_markup())

    elif mapping[text] == "helpdesk":
        set_state(uid,"helpdesk")
        await update.message.reply_text("Describe your issue. Use /cancel to return to menu.")
    elif mapping[text] == "admin":
        await update.message.reply_text("🔐 Admin Panel", reply_markup=admin_panel_markup())

    return True


# ---------- handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info("Start by %s (%s)", user.full_name, user.id)

    uid = user.id
    subscribe(uid)  # Automatically subscribe the user
    is_user_admin = is_admin(uid)

    welcome = "👋 Welcome to *AAES Study Bot*!"
    if exam_mode_active():  # ✅ Now imported
        days = exam_countdown()
        if days is not None:
            welcome += f"\n\n🚨 *Exam Mode* – T-Minus **{days}** day{'s' if days != 1 else ''}!"

    await update.message.reply_text(
        welcome + "\n\nUse the menu below anytime:",
        parse_mode="Markdown",
        reply_markup=persistent_menu(is_user_admin),
    )
# bot.py  (add these handlers)

async def addadmin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    try:
        new_id = int(ctx.args[0])
        if add_admin(new_id):
            await update.message.reply_text(f"✅ Added admin `{new_id}`")
        else:
            await update.message.reply_text("ℹ️ That user is already an admin.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/addadmin <user_id>`")

async def removeadmin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    try:
        rem_id = int(ctx.args[0])
        if remove_admin(rem_id):
            await update.message.reply_text(f"✅ Removed admin `{rem_id}`")
        else:
            await update.message.reply_text("ℹ️ That user was not an admin.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/removeadmin <user_id>`")
async def myid_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your Telegram user ID is: `{update.effective_user.id}`")

async def reset_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    CONVERSATION.pop(uid, None)
    await update.message.reply_text("🧠 Conversation history cleared.")

# Function to read text content from a DOCX file
def read_docx_file(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

async def send_about_aaes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # Define the file paths
    about_aaes_file_path = 'data/about_aaes.docx'
    logo_path = 'data/aaes_logo.jpg'

    # Check if the DOCX file exists
    if not os.path.exists(about_aaes_file_path):
        await q.edit_message_text("The 'About AAES' information file is missing.", parse_mode="Markdown")
        return

    # Read the text content from the DOCX file
    about_aaes_text = read_docx_file(about_aaes_file_path)

    # Send the text content
    await q.edit_message_text(about_aaes_text, parse_mode="Markdown")

    # Check if the logo file exists
    if os.path.exists(logo_path):
        await context.bot.send_photo(chat_id=q.message.chat_id, photo=open(logo_path, 'rb'))
    else:
        await context.bot.send_message(chat_id=q.message.chat_id, text="Logo image not found.")

def create_executive_buttons():
    kb = []
    for idx, officer in enumerate(executives):          # ← officer instead of exec
        kb.append([InlineKeyboardButton(officer["position"], callback_data=f"exec_info:{idx}")])
    return InlineKeyboardMarkup(kb)

async def send_executive_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # Extract the index of the executive from the callback data
    exec_index = int(q.data.split(":")[1])
    exec_info = executives[exec_index]

    # Prepare the message text
    message_text = (
        f"*Name:* {exec_info['name']}\n"
        f"*Class:* {exec_info['class']}\n"
        f"*Position:* {exec_info['position']}\n"
        f"*Duty:* {exec_info['duty']}"
    )

    # Send the message with the executive's information
    await q.edit_message_text(message_text, parse_mode="Markdown")

    # Send the executive's photo
    if os.path.exists(exec_info["photo_path"]):
        await context.bot.send_photo(chat_id=q.message.chat_id, photo=open(exec_info["photo_path"], 'rb'))
    else:
        await context.bot.send_message(chat_id=q.message.chat_id, text="Photo not available.")

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

async def upload_file_to_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = 'path/to/your/file.pdf'  # Replace with your file path
    chat_id = update.effective_chat.id

    try:
        with open(file_path, 'rb') as file:
            sent_file = await context.bot.send_document(chat_id=chat_id, document=file)
            file_id = sent_file.document.file_id
            logger.info(f"File ID: {file_id}")
            return file_id
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Failed to upload file.")

async def send_drive_file(file_id, filename, bot, chat_id, caption=""):
    try:
        drive_service = get_drive_service()

        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)

        mime, _ = mimetypes.guess_type(filename)
        if not mime:
            mime = "application/octet-stream"

        file_size = fh.getbuffer().nbytes
        if file_size > 49 * 1024 * 1024:  # 49 MB safety margin
            file = drive_service.files().get(fileId=file_id, fields="webViewLink").execute()
            link = file.get("webViewLink", "https://drive.google.com")
            await bot.send_message(
                chat_id=chat_id,
                text=f"📁 *{filename}* is too large for Telegram.\n\n[Download here]({link})",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return

        await bot.send_document(
            chat_id=chat_id,
            document=InputFile(fh, filename=filename),
            caption=caption or "",
            parse_mode=ParseMode.MARKDOWN,
            read_timeout=300,
            write_timeout=300,
        )

    except Exception as e:
        logger.error(f"Failed to send file: {e}")
        try:
            file = drive_service.files().get(fileId=file_id, fields="webViewLink").execute()
            link = file.get("webViewLink", "https://drive.google.com")
            await bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ Could not send *{filename}* directly.\n\n[Download here]({link})",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e2:
            logger.error(f"Fallback link also failed: {e2}")
            await bot.send_message(chat_id=chat_id, text="❌ File unavailable.")


async def ping_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "/ping":
        await update.message.reply_text("🏓 still alive")
#-----callback router -----

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    code = q.data
    uid = q.from_user.id

    if code == "menu":
        await q.edit_message_text("Main menu", reply_markup=InlineKeyboardMarkup([]))
        await context.bot.send_message(
            chat_id=q.message.chat_id,
            text="Choose an option:",
            reply_markup=persistent_menu(),
        )
        return

    if code == "ask_ai":
        set_state(uid, "ask")
        await q.edit_message_text("Type your question or upload slides. Use /cancel to return.")
        return

    if code == "materials":
        await q.edit_message_text("Choose level", reply_markup=materials_menu_markup())
        return

    if code == "materials_global":
        set_state(uid,"global_search")
        await q.edit_message_text("Type anything to search all slides and past questions. Use /cancel to return.")
        return

    if code.startswith("level_"):
        USER_STATE[uid] = code
        await q.edit_message_text("Choose resource type", reply_markup=materials_type_markup())
        return

    if code == "materials_slides":
        set_state(uid,"search_slides")
        await q.edit_message_text("Type the course name or code to find slides. Use /cancel to return.")
        return

    if code == "materials_pastq":
        set_state(uid,"search_pastq")
        await q.edit_message_text("Type the course name or code to find past questions. Use /cancel to return.")
        return

    if code == "announcements":
        data = load_announcements()
        if not data:
            await q.edit_message_text("No announcements yet.", reply_markup=InlineKeyboardMarkup([]))
        else:
            from announcements import format_announcements_pretty
            text = format_announcements_pretty(10)
            await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([]))
        await context.bot.send_message(
            chat_id=q.message.chat_id,
            text="Choose an option:",
            reply_markup=persistent_menu(),
        )
        return

        # ---------- internship alerts ----------
    if code == "internship_alerts":
        from internship_alerts import last_n
        alerts = last_n(5)
        if not alerts:
            text = "No internship or sponsorship alerts yet."
        else:
            text = "💼 *Latest Internship & Sponsorship Alerts*\n\n" + "\n\n".join(
                    f"• {a}" for a in alerts
                )
            kb = [[InlineKeyboardButton("Back ◀️", callback_data="announcements")]]
            await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
            return
    if code == "toolkit":
        await q.edit_message_text("Toolkit", reply_markup=toolkit_menu_markup())
        return

            # ---------- skill flow ----------

    if code == "toolkit_skill":
        skills = list_skills()
        kb = [[InlineKeyboardButton(s.title(), callback_data=f"skillpick_{s}")] for s in skills]
        kb.append([InlineKeyboardButton("Back ◀️", callback_data="toolkit")])
        await q.edit_message_text("Choose a skill to learn:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if code.startswith("skillpick_"):
        skill = code.split("_", 1)[1]
        lessons = get_lessons(skill)
        if not lessons:
            await q.edit_message_text("No lessons found for this skill.")
            return
        uid = q.from_user.id
        prog = get_progress(uid).get(skill, {}).get("last", -1)
        kb = []
        for idx, les in enumerate(lessons):
            label = f"Lesson {idx+1}"
            if idx <= prog:
                label += " ✅"
            kb.append([InlineKeyboardButton(label, callback_data=f"skilllesson_{skill}_{idx}")])
        if prog >= 0 and prog < len(lessons)-1:
            kb.append([InlineKeyboardButton("▶️ Continue", callback_data=f"skilllesson_{skill}_{prog+1}")])
            kb.append([InlineKeyboardButton("ℹ️ About this skill", callback_data=f"skillabout_{skill}")])
        await q.edit_message_text(f"{skill.title()} – pick a lesson:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if code.startswith("skillabout_"):
        skill = code.split("_", 1)[1]
        logger.info("Fetching intro for skill %s", skill)
        caption, thumb = fetch_skill_intro(skill)
        logger.info("fetch_skill_intro returned caption=%s thumb=%s", caption, thumb)
        if not caption and not thumb:
            await q.answer("No intro available for this skill.")
            return
    #send photo with caption.
        if thumb:
            await context.bot.send_photo(chat_id=q.message.chat_id,photo=open(thumb,"rb"),caption=caption,parse_mode="Markdown")
            try:
                os.remove(thumb)
            except Exception:
                pass
        else:
            await context.bot.send_message(chat_id=q.message.chat_id,text=caption,parse_mode="Markdown")
        return

    if code.startswith("skilllesson_"):
        _, skill, idx_str = code.split("_", 2)
        idx = int(idx_str)
        lessons = get_lessons(skill)
        if idx >= len(lessons):
            await q.answer("Lesson not found")
            return
        lesson = lessons[idx]
        # send file
        await q.answer("Opening lesson…")
        from skill_engine import get_skill_intro
        caption, thumb = get_skill_intro(skill)
        await send_drive_file(
            lesson["id"],
            lesson["name"],
            context.bot,
            q.message.chat_id,
            caption=caption,
            thumb_path=thumb
        )
# optional clean-up
        if thumb and os.path.exists(thumb):
            try:
                os.remove(thumb)
            except Exception:
                pass
        # ask to mark done
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Mark Done", callback_data=f"skilldone_{skill}_{idx}")],
            [InlineKeyboardButton("Back", callback_data=f"skillpick_{skill}")]
        ])
        await context.bot.send_message(
            chat_id=q.message.chat_id,
            text=f"Lesson {idx+1} of *{skill.title()}* sent.\nTap **Mark Done** when finished.",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return

    if code.startswith("skilldone_"):
        _, skill, idx_str = code.split("_", 2)
        idx = int(idx_str)
        uid = q.from_user.id
        set_progress(uid, skill, idx)
        # micro-reward
        rewards = ["🎉 Great job!", "💪 Keep going!", "🚀 Progress saved!", "🏅 Lesson complete!"]
        await q.answer(random.choice(rewards), show_alert=True)
        # quiz?
        quiz = get_quiz(skill, idx)
        if quiz:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(opt, callback_data=f"skillquiz_{skill}_{idx}_{i}")]
                for i, opt in enumerate(quiz["o"])
            ])
            await context.bot.send_message(
                chat_id=q.message.chat_id,
                text=f"Quick check:\n{quiz['q']}",
                reply_markup=kb
            )
        else:
            # back to skill menu
            await callback_router(Update(
                update_id=0,
                callback_query=type("CQ", (), {"data": f"skillpick_{skill}", "from_user": q.from_user, "message": q.message})
            ), context)
        return

    if code.startswith("skillquiz_"):
        _, skill, idx_str, choice_str = code.split("_", 3)
        idx = int(idx_str)
        choice = int(choice_str)
        quiz = get_quiz(skill, idx)
        if not quiz:
            await q.answer("No quiz found")
            return
        correct = quiz["a"]
        if choice == correct:
            await q.answer("✅ Correct!", show_alert=True)
        else:
            await q.answer(f"❌ Correct answer: {quiz['o'][correct]}", show_alert=True)
        # back to skill menu
        await callback_router(Update(
            update_id=0,
            callback_query=type("CQ", (), {"data": f"skillpick_{skill}", "from_user": q.from_user, "message": q.message})
        ), context)
        return

    if code.startswith("sendfile_"):
        file_id = code.replace("sendfile_", "")
        filename = file_id
        try:
            for row in q.message.reply_markup.inline_keyboard:
                for btn in row:
                    if btn.callback_data == code:
                        filename = btn.text.split(" (")[0][2:]
                        break
        except Exception:
            pass
        await q.answer("Sending file …")
        try:
            await send_drive_file(file_id, filename, context.bot, q.message.chat_id)
        except Exception as e:
            logger.error(e)
            await q.edit_message_text("File too large or unavailable.")
        return

    if code == "toolkit_gpa":
        await q.edit_message_text(
            "Choose GPA type:", reply_markup=gpa_type_markup()
        )
        return

    if code in ("gpa_semester", "gpa_cumulative"):
        USER_STATE[uid] = f"gpa_{code.split('_')[1]}"
        guide = (
            "Send your results in this format (one per line):\n"
            "`Course, Grade/Mark, Credits`\n"
            "Examples:\n"
            "Chemistry, 85, 3\n"
            "Math, B, 4\n"
            "Physics, 72, 2\n\n"
            "You can type or upload a file (.txt/.csv/.docx/.pdf)"
        )
        await q.edit_message_text(guide, parse_mode="Markdown")
        return

            # ---------- formulas ----------
    if code == "toolkit_formulas":
            from formula_reference import category_buttons
            await q.edit_message_text(
                "Pick a category to view formulas:",
                reply_markup=category_buttons()
            )
            return

    if code.startswith("formcat_"):
            cat = code[8:]
            from formula_reference import format_formula_list, get_formulas, formula_detail_buttons
            formulas = get_formulas(cat)
            if not formulas:
                await q.edit_message_text(
                    "No formulas in this category yet.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Back ◀️", callback_data="toolkit_formulas")]
                    ])
                )
                return
            # Show first formula
            f = formulas[0]
            text = f"*{cat}* – 1/{len(formulas)}\n\n" \
                   f"*{f['name']}*\n`{f['expression']}`"
            if f["explanation"]:
                text += f"\n\n_{f['explanation']}_"
            await q.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=formula_detail_buttons(cat, 0)
            )
            return

    if code.startswith("formnav_"):
            _, cat, idx_str = code.split("_", 2)
            idx = int(idx_str)
            from formula_reference import get_formulas, formula_detail_buttons
            formulas = get_formulas(cat)
            if idx < 0 or idx >= len(formulas):
                await q.answer("Out of range")
                return
            f = formulas[idx]
            text = f"*{cat}* – {idx+1}/{len(formulas)}\n\n" \
                   f"*{f['name']}*\n`{f['expression']}`"
            if f["explanation"]:
                text += f"\n\n_{f['explanation']}_"
            await q.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=formula_detail_buttons(cat, idx)
            )
            return
    if code == "show_calendar":
        calendar_id = "YOUR_CALENDAR_IMAGE_FILE_ID_FROM_DRIVE"  # or upload to Drive and get ID
        try:
            await context.bot.send_photo(
                chat_id=q.message.chat_id,
                photo=calendar_id,
                caption="📅 *KNUST Academic Calendar*",
                parse_mode="Markdown"
           )
        except Exception:
            await q.answer("Calendar not available", show_alert=True)
        return

    if code == "toolkit_timetable":
        set_state(uid,"await_courses")
        await q.edit_message_text(
            "Send your courses in this format:\n"
            "`Course Code, Credits`\n"
            "Example:\n"
            "ME 461, 3\n"
            "AE 301, 2"
            "\n\nYou can type or upload a file (.txt/.csv/.docx/.pdf)",
        )
        return

    if code.startswith("fact_"):
        fact = code.split("_", 1)[1]
        await q.answer("Processing your request...")
        await q.edit_message_text(
            f"✈️ *Daily Flight Log*\n\n{fact}\n\n*Want to know more?*",
            parse_mode="Markdown",
            reply_markup=None
        )
        await q.message.reply_text(
            "🔍 *Looking through slides…*  _This’ll take a sec._",
            parse_mode="Markdown"
        )
        try:
            answer = await ai_chat_response(fact)
            await q.message.reply_text(answer, parse_mode="Markdown")
        except Exception as e:
            logger.exception("AI response failed")
            await q.message.reply_text("❌ I couldn’t generate an answer. Try a shorter question or upload slides.")

#---------- AAES Hub ----------
    if code == "hub":
        await q.edit_message_text("AAES Hub", reply_markup=hub_menu_markup())
        return

    if code == "hub_about":
        await send_about_aaes(update, context)
        return

    if code == "hub_execs":
        # Send the inline keyboard with executive buttons
        await q.edit_message_text("Meet the Execs", reply_markup=create_executive_buttons())
        return

    if code.startswith("exec_info:"):
        await send_executive_info(update, context)
        return


    if code == "hub_activity":
        acts = get_user_activity(uid)
        if not acts:
            await q.edit_message_text("You have no recent activity.", reply_markup=hub_menu_markup())
        else:
            out = "Recent activity:\n" + "\n".join(f"- {a}" for a in acts)
            await q.edit_message_text(out, reply_markup=hub_menu_markup())
        return


    if code == "helpdesk":
        set_state(uid,"helpdesk")
        await q.edit_message_text("Describe your issue. Use /cancel to return to menu.")
        return

        # ---------- admin panel ----------
    if code == "admin_announce":
        USER_STATE[uid] = "admin_announce"
        await q.edit_message_text("Type the announcement text. /cancel to abort.")
        return

    if code == "admin_internship":
        USER_STATE[uid] = "admin_internship"
        await q.edit_message_text("Type the internship/sponsorship text. /cancel to abort.")
        return

    if code == "admin_fact":
        USER_STATE[uid] ="admin_fact"
        await q.edit_message_text("Type the new Daily Flight Log fact. /cancel to abort.")
        return

    if code == "admin_add":
        USER_STATE[uid] ="admin_add"
        await q.edit_message_text("Send the Telegram user ID to promote. /cancel to abort.")
        return

    if code == "admin_toggle_exam":
        from exam_mode import exam_mode_active, activate_exam_mode, deactivate_exam_mode, exam_countdown
        if exam_mode_active():
            deactivate_exam_mode()
            text = "📘 Exam Mode is now **OFF**."
            await q.edit_message_text(text, reply_markup=admin_panel_markup())
        else:
            USER_STATE[uid] = "await_exam_date"
            await q.edit_message_text(
                "📅 Send the exam date in format `YYYY-MM-DD` (e.g., 2025-05-10)\n/cancel to abort.",
            parse_mode="Markdown"
            )
        return

    if code == "admin_remove":
        USER_STATE[uid] ="admin_remove"
        await q.edit_message_text("Send the Telegram user ID to demote. /cancel to abort.")
        return

    if code == "admin_subs":
        from notify import list_subscribers
        n = len(list_subscribers())
        await q.edit_message_text(f"📊 {n} users are subscribed.", reply_markup=admin_panel_markup())
        return

    if code == "admin_tickets":
        from helpdesk import format_tickets_with_buttons
        text, markup = format_tickets_with_buttons(limit=10)
        await q.edit_message_text(text, reply_markup=markup)
        return

    if code.startswith("resolve_ticket_"):
        idx = int(code.split("_")[-1])
        from helpdesk import resolve_ticket
        ticket = resolve_ticket(idx)
        if ticket:
            await q.answer(f"Ticket #{idx} marked resolved ✅", show_alert=True)
            # Re-show the list
            from helpdesk import format_tickets_with_buttons
            text, markup = format_tickets_with_buttons(limit=10)
            await q.edit_message_text(text, reply_markup=markup)
        else:
            await q.answer("Ticket not found ❌", show_alert=True)
        return

# ---------- text / document handlers ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    uid = update.effective_user.id
    name = update.effective_user.full_name

    try:
        log_activity(uid, f"sent: {text}")
        update_streak(uid)
    except Exception:
        logger.debug("Activity log failed")

    if await route_persistent_text(update, context):
        return

    if text.lower() == "/cancel":
        USER_STATE.pop(uid, None)
        await update.message.reply_text("Cancelled", reply_markup=persistent_menu())
        return

    if text.lower().startswith("/search "):
        term = text.split(" ", 1)[1].strip()
        folder_id = _find_folder_id(term)
        files = _files_in_folder(folder_id) if folder_id else search_drive(term, mode="all", level=None)
        if not files:
            await update.message.reply_text("No matching folder or files found.", reply_markup=persistent_menu())
            return
        kb = []
        for f in files[:15]:
            size_mb = round(int(f.get("size", 0)) / 1024 / 1024, 1)
            kb.append([
                InlineKeyboardButton(f"📄 {f['name']} ({size_mb} MB)", callback_data=f"sendfile_{f['id']}")
            ])
        await update.message.reply_text(f"Found {len(files)} file(s):", reply_markup=InlineKeyboardMarkup(kb))
        return

    if text == "GPA Calculator 📊" or USER_STATE.get(uid) == "toolkit_gpa":
        set_state(uid,"toolkit_gpa")
        await gpa_flow(update, context)
        return

    if USER_STATE.get(uid) == "helpdesk":
        add_ticket(uid, name, text)
        USER_STATE.pop(uid, None)
        await update.message.reply_text("Thanks. Your issue is logged. Execs will follow up.", reply_markup=persistent_menu())
        return

    state = get_state(uid).get("state")
    if state in ("search_slides", "search_pastq", "global_search"):
        level = None
        mode = "all"
        if state == "search_slides":
            mode = "slides"
            for k in ("level_100", "level_200", "level_300", "level_400"):
                if USER_STATE.get(uid) == k:
                    level = k.split("_")[1]
                    break
        elif state == "search_pastq":
            mode = "pastq"

        query = text.strip()
        folder_id = _find_folder_id(query)
        files = _files_in_folder(folder_id) if folder_id else search_drive(query, mode=mode, level=level)
        USER_STATE.pop(uid, None)

        if not files:
            await update.message.reply_text("No matching folder or files found.", reply_markup=persistent_menu())
            return

        kb = []
        for f in files[:15]:
            size_mb = round(int(f.get("size", 0)) / 1024 / 1024, 1)
            kb.append([
                InlineKeyboardButton(f"📄 {f['name']} ({size_mb} MB)", callback_data=f"sendfile_{f['id']}")
            ])
        await update.message.reply_text(f"Found {len(files)} file(s):", reply_markup=InlineKeyboardMarkup(kb))
        return

    if USER_STATE.get(uid) == "await_courses":
        try:
            courses = []
            for line in text.splitlines():
                code, cred = line.split(",")
                courses.append({"code": code.strip(), "credits": int(cred.strip())})
            from timetable_generator import generate_timetable
            timetable = generate_timetable(courses)
            await update.message.reply_text(timetable, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text("❌ Invalid format. Use: `Course, Credits`")
        USER_STATE.pop(uid, None)
        return

    # admin panel text inputs
    admin_state = USER_STATE.get(uid)
    if admin_state and admin_state.startswith("admin_"):
        if not is_admin(uid):
            await update.message.reply_text("❌ Not authorized.")
            USER_STATE.pop(uid, None)
            return

        text_in = update.message.text.strip()
        if text_in.lower() == "/cancel":
            USER_STATE.pop(uid, None)
            await update.message.reply_text("Cancelled.", reply_markup=persistent_menu(is_admin(uid)))
            return

        if USER_STATE.get(uid) == "admin_announce":
            text = update.message.text.strip()
            if not text:
                await update.message.reply_text("Usage: /announce <message>")
                return
            add_announcement(text)
            subs = list_subscribers()
            count = 0
            for s in subs:
                try:
                    await context.bot.send_message(chat_id=int(s), text=f"📢 {text}")
                    count += 1
                except Exception:
                    pass
            await update.message.reply_text(f"Posted and sent to {count} subscribers.")
            USER_STATE.pop(uid, None)
            return

        if USER_STATE.get(uid) == "admin_internship":
            text = update.message.text.strip()
            if not text:
                await update.message.reply_text("Usage: /postinternship <text>")
                return
            from internship_alerts import add_alert
            add_alert(text, update.effective_user.id)
            subs = list_subscribers()
            count = 0
            for s in subs:
                try:
                    await context.bot.send_message(
                        chat_id=int(s),
                        text=f"💼 *Internship / Sponsorship Alert*\n\n{text}",
                        parse_mode="Markdown"
                    )
                    count += 1
                except Exception:
                    pass
            await update.message.reply_text(f"✅ Alert posted and broadcast.")
            USER_STATE.pop(uid, None)
            return

        if USER_STATE.get(uid) == "admin_fact":
            text = update.message.text.strip()
            if not text:
                await update.message.reply_text("Usage: /addfact <fact>")
                return
            from daily_flight_log import add_fact
            add_fact(text)
            await update.message.reply_text("✅ Fact added to pool.")
            USER_STATE.pop(uid, None)
            return

        if USER_STATE.get(uid) == "admin_add":
            try:
                new_id = int(update.message.text.strip())
                from admin import add_admin
                if add_admin(new_id):
                    await update.message.reply_text(f"✅ Added admin `{new_id}`")
                else:
                    await update.message.reply_text("ℹ️ Already an admin.")
            except ValueError:
                await update.message.reply_text("❌ Send a numeric user ID.")
            USER_STATE.pop(uid, None)
            return

        if USER_STATE.get(uid) == "admin_remove":
            try:
                rem_id = int(update.message.text.strip())
                from admin import remove_admin
                if remove_admin(rem_id):
                    await update.message.reply_text(f"✅ Removed admin `{rem_id}`")
                else:
                    await update.message.reply_text("ℹ️ Not an admin.")
            except ValueError:
                    await update.message.reply_text("❌ Send a numeric user ID.")
            USER_STATE.pop(uid, None)
            return

    if USER_STATE.get(uid, "").startswith("gpa_"):
        gpa_type = USER_STATE[uid].split("_")[1]  # semester | cumulative
        lines = text.splitlines()
        try:
            gpa, qp, creds = calculate_gpa(lines)
            await update.message.reply_text(
                f"✅ *{gpa_type.capitalize()} GPA*: **{gpa}**\n"
                f"Total Quality Points: {qp}\n"
                f"Total Credits: {creds}",
                parse_mode="Markdown",
                reply_markup=persistent_menu(),
            )
        except ValueError as e:
            await update.message.reply_text(f"❌ Error: {e}")
        USER_STATE.pop(uid, None)
        return

    # ---------- exam mode ----------
    if USER_STATE.get(uid) == "await_exam_date":
        try:
            from datetime import datetime
            date_str = text.strip()
            datetime.fromisoformat(date_str)  # validate format
            from exam_mode import activate_exam_mode
            activate_exam_mode(date_str)
            USER_STATE.pop(uid, None)
            await update.message.reply_text(
                f"✅ Exam Mode activated!\n📅 Countdown started for **{date_str}**.",
                reply_markup=persistent_menu(is_admin(uid))
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid date. Use format `YYYY-MM-DD`.")
        return

    # ---------- AI chat ----------
        # ---------- AI chat ----------
       # ---------- AI chat ----------
    state = get_state(uid).get("state")
    if state == "ask":
        add_turn(uid, "user", text)
        await update.message.reply_text("🔍 *Thinking…*", parse_mode="Markdown")
        try:
            answer = await ai_chat_response(build_prompt(uid))
            add_turn(uid, "assistant", answer)
            pretty = prettify_answer(answer)
            await update.message.reply_text(pretty, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception as e:
            logger.exception("AI response failed")
            await update.message.reply_text("❌ I couldn’t generate an answer. Try a shorter question or upload slides.")
        return

    # Send daily quiz if exam mode is active
    if exam_mode_active() and should_send_quiz_today():
        quiz = get_daily_quiz()
        for uid in list_subscribers():
            try:
                await app.bot.send_message(
                    int(uid),
                    f"📘 *Daily Exam Quiz*\n\n{quiz}\n\nReply with your answer!",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.warning("Daily quiz failed for %s: %s", uid, e)
        mark_quiz_sent()


async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    uid = update.effective_user.id

    if not doc:
        await update.message.reply_text("Send a PDF or DOCX file.")
        return
    if doc.file_size and doc.file_size > 15 * 1024 * 1024:  # 15 MB limit
        await update.message.reply_text("File too large. Send a file below 15 MB.")
        return

    try:
        log_activity(uid, f"uploaded {doc.file_name}")
        await handle_upload(doc, update)
        file_content = await read_file_content(doc.file_path)

        # grab the last user message (if any)
        history = CONVERSATION.get(uid, [])
        last_question = next((m["text"] for m in reversed(history) if m["role"] == "user"), None)

        if not last_question:
            await update.message.reply_text(
                "❗ Ask a question first, then upload the file.", parse_mode="Markdown"
            )
            return

        add_turn(uid, "user", last_question, file_content)   # store file with question
        await update.message.reply_text("📄 *Reading file…*", parse_mode="Markdown")

        try:
            answer = await ai_chat_response(build_prompt(uid))
            add_turn(uid, "assistant", answer)
            pretty = prettify_answer(answer)
            await update.message.reply_text(pretty, parse_mode="Markdown")
        except Exception as e:
            logger.exception("File AI failed")
            await update.message.reply_text("❌ I couldn’t generate an answer. Try a shorter question or upload slides.")
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("Failed to process the file.")



    if USER_STATE.get(uid, "").startswith("gpa_"):
        gpa_type = USER_STATE[uid].split("_")[1]
        try:
            text = read_file
            lines = text.splitlines()
            gpa, qp, creds = calculate_gpa(lines)
            await update.message.reply_text(
                f"✅ *{gpa_type.capitalize()} GPA*: **{gpa}**\n"
                f"Total Quality Points: {qp}\n"
                f"Total Credits: {creds}",
                parse_mode="Markdown",
                reply_markup=persistent_menu(),
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Could not parse file: {e}")
        USER_STATE.pop(uid, None)
        return

# ---------- commands ----------
async def announce_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("You are not an admin.")
        return

    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /announce <message>")
        return
    add_announcement(text)
    subs = list_subscribers()
    count = 0
    for s in subs:
        try:
            await context.bot.send_message(chat_id=int(s), text=f"AAES Announcement\n\n{text}")
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"Posted and sent to {count} subscribers.")

async def join_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    subscribe(uid)
    await update.message.reply_text("You will receive AAES announcements. Use /leave to stop.")

async def leave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    unsubscribe(uid)
    await update.message.reply_text("You will not receive announcements.")

async def execs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /execs_list to view execs. Admins can update profiles with /setprofile.")

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    p = get_profile(uid)
    if not p:
        await update.message.reply_text("No profile found. Use /setprofile name|program|level")
        return
    out = f"Name: {p.get('name','-')}\nProgram: {p.get('program','-')}\nLevel: {p.get('level','-')}"
    await update.message.reply_text(out)

async def setprofile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split(" ", 1)
    if len(parts) < 2:
        await update.message.reply_text("Usage: /setprofile name|program|level")
        return
    payload = parts[1].split("|")
    if len(payload) < 3:
        await update.message.reply_text("Provide name, program and level separated by |")
        return
    uid = update.effective_user.id
    update_profile(uid, "name", payload[0].strip())
    update_profile(uid, "program", payload[1].strip())
    update_profile(uid, "level", payload[2].strip())
    await update.message.reply_text("Profile updated.")
# bot.py
async def postinternship_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Not authorized.")
        return
    text = " ".join(ctx.args).strip()
    if not text:
        await update.message.reply_text("Usage: `/postinternship <text>`")
        return
    from internship_alerts import add_alert
    add_alert(text, update.effective_user.id)
    # broadcast
    from notify import list_subscribers
    for uid in list_subscribers():
        try:
            await ctx.bot.send_message(
                int(uid),
                f"💼 *Internship / Sponsorship Alert*\n\n{text}",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    await update.message.reply_text("✅ Alert posted and broadcast.")


# ---------- GPA flow ----------
GPA_STATE = {}   # uid -> {"step": 1..n, "courses": []}

async def gpa_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in GPA_STATE:
        GPA_STATE[uid] = {"step": 1, "courses": []}
        await update.message.reply_text("How many courses did you take? (send a number)")
        return

    state = GPA_STATE[uid]

    if state["step"] == 1:
        try:
            n = int(text)
            state["n"] = n
            state["step"] = 2
            await update.message.reply_text("Send grade and credit for course 1 in the format:\nA 3")
        except ValueError:
            await update.message.reply_text("Please send a valid number.")
        return

    if state["step"] == 2:
        try:
            grade, credit = text.upper().split()
            credit = int(credit)
            state["courses"].append((grade, credit))
            if len(state["courses"]) == state["n"]:
                grade_map = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
                total_points = sum(grade_map.get(g, 0) * c for g, c in state["courses"])
                total_credits = sum(c for _, c in state["courses"])
                gpa = total_points / total_credits if total_credits else 0
                await update.message.reply_text(f"Your GPA is **{gpa:.2f}**", parse_mode="Markdown", reply_markup=persistent_menu())
                del GPA_STATE[uid]
            else:
                await update.message.reply_text(f"Send grade and credit for course {len(state['courses'])+1}:")
        except Exception:
            await update.message.reply_text("Use format: A 3")
        return

async def continue_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    prog = get_progress(uid)
    if not prog:
        await update.message.reply_text("You haven't started any skill yet.")
        return
    # pick the skill with the highest last lesson
    skill, data = max(prog.items(), key=lambda x: x[1]["last"])
    last = data["last"]
    lessons = get_lessons(skill)
    if last >= len(lessons) - 1:
        await update.message.reply_text("You've already finished this skill!")
        return
    next_idx = last + 1
    lesson = lessons[next_idx]
    await send_drive_file(lesson["id"], lesson["name"], context.bot, update.effective_chat.id)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Mark Done", callback_data=f"skilldone_{skill}_{next_idx}")],
        [InlineKeyboardButton("Back", callback_data=f"skillpick_{skill}")]
    ])
    await update.message.reply_text(
        f"Resuming *{skill.title()}* – Lesson {next_idx+1}",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def addquiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ Not authorized.")
        return

    question = " ".join(context.args).strip()
    if not question:
        await update.message.reply_text("Usage: `/addquiz <question>`")
        return

    from exam_mode import add_quiz
    add_quiz(question)
    await update.message.reply_text("✅ Quiz question added to pool.")

# bot.py
async def addfact_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Not authorized.")
        return
    fact = " ".join(ctx.args).strip()
    if not fact:
        await update.message.reply_text("Usage: `/addfact <fact>`")
        return
    from daily_flight_log import add_fact
    add_fact(fact)
    await update.message.reply_text("✅ Fact added to pool.")

async def tickets_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Not authorized.")
        return
    from helpdesk import format_tickets
    await update.message.reply_text(format_tickets(limit=10))

    # ---------- scheduler integration ----------

# ---------- scheduler integration (CLEAN) ----------
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from daily_flight_log import get_daily_fact, should_send_fact, mark_fact_sent
from notify import list_subscribers

# Create scheduler instance
scheduler = AsyncIOScheduler()

from telegram import InlineKeyboardButton,InlineKeyboardMarkup

# ---------- daily flight log ----------
async def send_daily_flight_log(app):
    logger.info("Daily flight log job triggered")
    if not should_send_fact():
        logger.info("Daily flight log is disabled today")
        return

    fact = get_daily_fact()
    logger.info(f"Fact to be sent: {fact}")
    subscribers = list_subscribers()
    logger.info(f"Sending daily flight log to {len(subscribers)} subscribers")

    for uid in subscribers:
        try:
            # Encode the fact text in callback_data
            encoded_fact = encode_fact(fact)
            keyboard = [
                [InlineKeyboardButton("Want to know more?", callback_data=f"fact_more")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await app.bot.send_message(
                int(uid),
                fact,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            logger.ingo(f"Sent daily flight log to {uid}")
        except Exception as e:
            logger.warning(f"Failed to send daily fact to {uid}: {e}")

    mark_fact_sent()

async def post_init(application):
    """Initialize scheduler after bot is ready."""
    scheduler.add_job(
        send_daily_flight_log,
        'cron',
        hour=8,
        minute=0,
        args=[application]
    )
    scheduler.start()
    logger.info("Scheduler started - Daily Flight Log will send at 08:00")

executives = [
    {
        "name": "Elvis Owusu Osei",
        "class": "Aerospace Engineering",
        "position": "President",
        "duty": "Oversees all operations and represents the association.",
        "photo_path": "data/execs/President.png"
    },
    {
        "name": "Prince K. Fiador",
        "class": "Aerospace Engineering",
        "position": "Vice President",
        "duty": "Assists the President and manages internal affairs.",
        "photo_path": "data/execs/Vice President.png"
    },
    {
        "name": "Wendel A. Boadi",
        "class": "Automobile Engineering",
        "position": "General Secretary",
        "duty": "Responsible for maintaining records and managing correspondence, I ensure that all administrative tasks are handled efficiently.",
        "photo_path": "data/execs/General Secretary.png"
    },
    {
        "name": "Felix Junior Agyemang Odame",
        "class": "Aerospace Engineering",
        "position": "Financial Secretary",
        "duty": "I manage the financial affairs of AAES, ensuring transparency and accountability in our budgeting and spending",
        "photo_path": "data/execs/Financial Secretary.png"
    },
    {
        "name": "Kwadwo Nkansah Tannor ",
        "class": "Aerospace Engineering",
        "position": "Organizing Secretary",
        "duty": "Responsible for maintaining records and managing correspondence, I ensure that all administrative tasks are handled efficiently.",
        "photo_path": "data/execs/Organizing Secretary.png"
    },
    {
        "name": "Nathaniel Tawiah",
        "class": "Marine Engineering",
        "position": "Public Relations Officer",
        "duty": "I handle communications and outreach, promoting AAES and its activities to the wider community.",
        "photo_path": "data/execs/P.R.O.png"
    },
    # Add more executives as needed
]

# ---------- app builder ----------
def build_app():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
    app.add_handler(CommandHandler("announce", announce_cmd))
    app.add_handler(CommandHandler("join", join_cmd))
    app.add_handler(CommandHandler("leave", leave_cmd))
    app.add_handler(CommandHandler("execs", execs_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("setprofile", setprofile_cmd))
    app.add_handler(CommandHandler("continue", continue_cmd))
    app.add_handler(CommandHandler("addquiz", addquiz_cmd))
    app.add_handler(CommandHandler("addadmin", addadmin_cmd))
    app.add_handler(CommandHandler("removeadmin", removeadmin_cmd))
    app.add_handler(CommandHandler("myid", myid_cmd))
    app.add_handler(CommandHandler("addfact", addfact_cmd))
    app.add_handler(CommandHandler("postinternship", postinternship_cmd))
    app.add_handler(CommandHandler("tickets", tickets_cmd))
    app.add_handler(CommandHandler("ping", ping_me))
    app.add_handler(CommandHandler("reset", reset_cmd))
    from voice_handler import handle_voice
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    async def error_handler(update, context):
        import logging, traceback, os
        logging.error("Exception:", exc_info=context.error)
        dev_id = os.getenv("DEV_CHAT_ID")
        if dev_id:
            try:
                await context.bot.send_message(
                    chat_id=int(dev_id),
                    text=f"⚠️ Bot crash:\n```{traceback.format_exc()[-800:]}```",
                    parse_mode="Markdown"
            )
            except Exception:
                pass

    app.add_error_handler(error_handler)

    return app
app_flask = Flask(__name__)

@app_flask.route("/wake")
def wake():
    # send /ping to yourself via the bot
    bot.send_message(chat_id=1836471542, text="/ping")
    return "ok", 200

def run():
    app = build_app()
    logger.info("Bot starting")
    app.run_polling()

if __name__ == "__main__":
    run()