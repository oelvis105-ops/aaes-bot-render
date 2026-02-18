import os
import json
from ai_personality import build_response
from drive_search import search_drive
from user_memory import get_user_history
from file_ai import analyze_file
from openai_api import ask_model


# --------------------------------------------------
# MAIN AI RESPONSE PIPELINE
# --------------------------------------------------
async def ai_chat_response(question, file_path=None, user_id=None):
    history = get_user_history(user_id)

    slides_result = ""
    drive_result = ""

    if question:
        drive_result = search_drive(question)

    if file_path:
        slides_result = analyze_file(file_path)

    model_answer = await ask_model(
        question=question,
        history=history,
        files=slides_result
    )

    final = build_response(
        question,
        slides_result,
        drive_result,
        model_answer
    )

    return final