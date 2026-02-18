import os
from typing import List, Dict
from google_drive_skills import (
    SKILL_FOLDER_MAP,
    list_lessons_in_skill,
    count_lessons,
    get_lesson_link,
)

# Friendly names for users
SKILLS = [
    {"key": "SolidWorks", "label": "3D Modeling: SolidWorks"},
    {"key": "AutoCAD", "label": "3D Modeling: AutoCAD"},
    {"key": "Python", "label": "Python Programming"},
    {"key": "Arduino", "label": "Arduino Programming"},
    {"key": "MATLAB", "label": "Programming with MATLAB"},
    {"key": "Robotics", "label": "Robotics"},
    {"key": "Others", "label": "More Skills"},
]


def available_skills() -> List[str]:
    return [s["key"] for s in SKILLS]


def skill_label(key: str) -> str:
    for s in SKILLS:
        if s["key"] == key:
            return s["label"]
    return key


def skill_folder_id(key: str) -> str:
    return SKILL_FOLDER_MAP.get(key)


def list_skill_lessons(key: str) -> List[Dict]:
    """
    Returns list of lesson metadata for the skill key.
    Each entry contains name, id, link, lesson.
    """
    folder = skill_folder_id(key)
    if not folder:
        return []
    return list_lessons_in_skill(folder)


def skill_lesson_count(key: str) -> int:
    folder = skill_folder_id(key)
    if not folder:
        return 0
    return count_lessons(folder)


def lesson_button_list(key: str) -> List[Dict]:
    """
    Returns a list of button labels and callback ids that your bot can render.
    Example element: {'text': 'Lesson 1', 'callback_data': 'skilllesson_Python_1'}
    """
    lessons = list_skill_lessons(key)
    out = []
    for idx, item in enumerate(lessons):
        if item["lesson"] >= 10**6:
            continue
        text = f"Lesson {item['lesson']}"
        cb = f"skilllesson_{key}_{item['lesson']}"
        out.append({"text": text, "callback": cb})
    return out


def get_lesson_by_number(key: str, number: int) -> Dict:
    folder = skill_folder_id(key)
    if not folder:
        return None
    return get_lesson_link(folder, number)
