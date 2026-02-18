import os
import requests
from typing import List, Dict
import re

DRIVE_API_KEY = os.getenv("GOOGLE_DRIVE_API_KEY")

# Map skill folder ids if you want to override in code.
# You already provided these. Keep them here for convenience.
SKILL_FOLDER_MAP = {
    "SolidWorks": "1HV6SUgRKeuWQifUcsbDiBB5FybVmxzZk",
    "AutoCAD": "1om8NqWkTn0izG1i4FJKDPDehITMEGOc_",
    "Python": "1zh4EKKakJaggXki6tkTOimfdzLeGG64N",
    "Arduino": "1la4ALy-ENwAgJS1GGWMj5Z62TSyBczqS",
    "MATLAB": "1fNnEPnKFv92oAqJWvtTHgC7pWVIlIpde",
    "Robotics": "1vqeulDK0gMylQrQgL9bChcDWrjwMQkMd",
    "Others": "1vqeulDK0gMylQrQgL9bChcDWrjwMQkMd",
}

DRIVE_FILES_ENDPOINT = "https://www.googleapis.com/drive/v3/files"


def _list_folder_files(folder_id: str) -> List[Dict]:
    """
    Return list of files metadata in the folder_id.
    Uses the Drive v3 files list endpoint with an API key.
    """
    if not DRIVE_API_KEY:
        return []

    q = f"'{folder_id}' in parents and trashed = false"
    params = {
        "q": q,
        "fields": "files(id,name,mimeType,webViewLink,createdTime)",
        "pageSize": 1000,
        "key": DRIVE_API_KEY,
    }

    try:
        r = requests.get(DRIVE_FILES_ENDPOINT, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("files", [])
    except Exception:
        return []


def _lesson_number_from_name(name: str) -> int:
    """
    Extract lesson number from filename.
    Expect names like 'Lesson 1 ...' or 'lesson 2 - title'.
    Returns large number if not found so these sort last.
    """
    m = re.search(r"lesson\s*0*([0-9]+)", name, flags=re.I)
    if not m:
        return 10**6
    try:
        return int(m.group(1))
    except Exception:
        return 10**6


def list_lessons_in_skill(folder_id: str) -> List[Dict]:
    """
    Return sorted list of lesson files for a skill folder.
    Each entry: { 'name', 'id', 'link', 'lesson' }
    """
    files = _list_folder_files(folder_id)
    out = []
    for f in files:
        lesson_num = _lesson_number_from_name(f.get("name", ""))
        out.append(
            {
                "name": f.get("name"),
                "id": f.get("id"),
                "link": f.get("webViewLink") or f.get("id"),
                "lesson": lesson_num,
            }
        )

    out.sort(key=lambda x: x["lesson"])
    return out


def count_lessons(folder_id: str) -> int:
    files = list_lessons_in_skill(folder_id)
    # Count only those that look like lessons
    return sum(1 for f in files if f["lesson"] < 10**6)


def get_lesson_link(folder_id: str, lesson_index: int) -> Dict:
    """
    lesson_index is 1-based.
    Returns dict with name and link or None if not found.
    """
    lessons = list_lessons_in_skill(folder_id)
    lessons_only = [l for l in lessons if l["lesson"] < 10**6]
    if not lessons_only:
        return None
    if lesson_index < 1 or lesson_index > len(lessons_only):
        return None
    return lessons_only[lesson_index - 1]
