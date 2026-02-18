import os
import tempfile
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import ai_chat_response, add_turn, build_prompt

logger = logging.getLogger("aaes-bot")

# Choose your engine:
# Option A: OpenAI Whisper (requires OPENAI_API_KEY)
# Option B: Whisper.cpp (local, free)
# Option C: AssemblyAI (requires ASSEMBLYAI_API_KEY)

# === Option A: OpenAI Whisper (recommended for speed) ===
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

async def transcribe_voice(update: Update) -> str:
    voice = update.message.voice or update.message.audio
    if not voice:
        return ""

    tg_file = await voice.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
        path = tmp.name
    await tg_file.download_to_drive(path)

    try:
        with open(path, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)
        return transcript["text"].strip()
    except Exception as e:
        logger.error("Transcription failed: %s", e)
        return ""
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

# === Route voice messages ===
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = await transcribe_voice(update)
    if not text:
        await update.message.reply_text("❌ Could not understand the audio.")
        return

    # Treat it like a normal AI question
    add_turn(uid, "user", text)
    await update.message.reply_text("🔍 *Thinking…*", parse_mode="Markdown")
    try:
        answer = await ai_chat_response(build_prompt(uid))
        add_turn(uid, "assistant", answer)
        await update.message.reply_text(answer, parse_mode="Markdown")
    except Exception as e:
        logger.error("Voice AI failed: %s", e)
        await update.message.reply_text("❌ Could not process your question.")