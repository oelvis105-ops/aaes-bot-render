import re

# -----------------------------------------
# Classify tone from user question
# -----------------------------------------
def classify_tone(text):
    t = text.lower()

    if "explain" in t or "how" in t:
        return "technical"

    if "help" in t or "stuck" in t:
        return "supportive"

    if "joke" in t or "funny" in t:
        return "playful"

    if "motivate" in t or "tired" in t:
        return "motivational"

    return "neutral"


# -----------------------------------------
# Core personality rules
# -----------------------------------------
def apply_personality(tone, answer):
    if tone == "technical":
        return (
            "Here is a clear explanation.\n\n"
            + answer
            + "\n\nIf you want examples, ask again."
        )

    if tone == "supportive":
        return (
            "I understand what you are trying to figure out.\n\n"
            + answer
            + "\n\nTell me what part you want simplified."
        )

    if tone == "playful":
        return (
            "Alright, quick one.\n\n"
            + answer
        )

    if tone == "motivational":
        return (
            "You are doing fine. Keep going.\n\n"
            + answer
            + "\n\nLet me know if you want a study tip."
        )

    return answer


# -----------------------------------------
# Mixed strategy engine
# blend slides, search, memory and AI model
# -----------------------------------------
def mix_sources(slides, drive_hits, ai_text):
    parts = []

    if slides:
        parts.append("Slides reference:\n" + slides)

    if drive_hits:
        parts.append("Files found:\n" + drive_hits)

    if ai_text:
        parts.append("AI explanation:\n" + ai_text)

    return "\n\n".join(parts).strip()


# -----------------------------------------
# Safety cleaning
# -----------------------------------------
def clean(text):
    if text is None:
        return ""

    text = re.sub(r"http\S+", "", text)
    text = text.replace("<", "").replace(">", "")
    text = text.strip()
    return text


# -----------------------------------------
# Main personality wrapper
# -----------------------------------------
def build_response(question, slides_answer, drive_answer, model_answer):
    tone = classify_tone(question)

    merged = mix_sources(
        clean(slides_answer),
        clean(drive_answer),
        clean(model_answer)
    )

    return apply_personality(tone, merged)
