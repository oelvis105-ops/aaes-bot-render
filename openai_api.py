import os
from openai import OpenAI
from google_drive import search_drive


# ----------------------------------------------------
# Create AI client
# ----------------------------------------------------
def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in .env")
    return OpenAI(api_key=api_key)


client = get_client()


# ----------------------------------------------------
# Generate AI answer for user question
# ----------------------------------------------------
def ask_ai(prompt, drive_hint=True):
    try:
        drive_reference = ""

        # Attach relevant Drive materials automatically
        if drive_hint:
            ref = search_drive(prompt)
            if "No matching" not in ref:
                drive_reference = f"\n\nDrive Material:\n{ref}"

        system_message = (
            "You are AeroTutor, a helpful academic assistant for AAES students at KNUST. "
            "Use simple language and reference engineering knowledge. "
            "Always prioritise accuracy and clarity. If a Drive reference is provided, use it."
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt + drive_reference},
        ]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.4
        )

        return completion.choices[0].message.content.strip()

    except Exception:
        return "I could not generate a response at the moment."


# ----------------------------------------------------
# Ask AI with file content
# ----------------------------------------------------
def ask_ai_with_file(question, extracted_text):
    try:
        system_message = (
            "You are AeroTutor, an engineering assistant for AAES students. "
            "You are analysing content extracted from a file uploaded by the student. "
            "Explain using simple language and reference file content directly."
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "system", "content": f"File content:\n{extracted_text}"},
            {"role": "user", "content": question},
        ]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.4
        )

        return completion.choices[0].message.content.strip()

    except Exception:
        return "I could not analyse the file."


# ----------------------------------------------------
# Quick test helper
# ----------------------------------------------------
def ai_test():
    return ask_ai("Explain Bernoulli's principle in one sentence.")
