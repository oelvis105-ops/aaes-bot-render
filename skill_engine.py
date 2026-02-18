# skill_engine.py
import io
import tempfile
import os
from googleapiclient.http import MediaIoBaseDownload
import os, json, random
from datetime import datetime
from typing import List, Dict
from drive_search import _find_folder_id, _files_in_folder

SKILL_ROOT = {
    "arduino programming":   "1la4ALy-ENwAgJS1GGWMj5Z62TSyBczqS",   # ← replace with real Drive folder IDs
    "python programming":    "1zh4EKKakJaggXki6tkTOimfdzLeGG64N",
    "3dmodel with Solidworks":   "1HV6SUgRKeuWQifUcsbDiBB5FybVmxzZk",
    "3dmodel with AutoCAD":   "1om8NqWkTn0izG1i4FJKDPDehITMEGOc_",
    "drone":     "1j4-oqXqRZjM6k_fnFZX0bpB7VCc4n63Z",
    "robotics":  "1vqeulDK0gMylQrQgL9bChcDWrjwMQkMd",
    "programming with MathLab": "1fNnEPnKFv92oAqJWvtTHgC7pWVIlIpde"
}

QUIZ_PATH = "data/skill_quizzes.json"
PROGRESS_PATH = "data/skill_progress.json"
os.makedirs("data", exist_ok=True)

# ---------- helpers ----------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def list_skills() -> List[str]:
    return list(SKILL_ROOT.keys())

def get_lessons(skill: str) -> List[Dict]:
    folder_id = SKILL_ROOT.get(skill)
    if not folder_id:
        return []
    files = _files_in_folder(folder_id)
    # sort by filename prefix 01, 02, ...
    files.sort(key=lambda f: f["name"])
    return [{"id": f["id"], "name": f["name"], "link": f["link"]} for f in files]

def get_progress(uid: int) -> Dict:
    return load_json(PROGRESS_PATH, {}).get(str(uid), {})

def set_progress(uid: int, skill: str, lesson_idx: int):
    prog = load_json(PROGRESS_PATH, {})
    uid_str = str(uid)
    if uid_str not in prog:
        prog[uid_str] = {}
    prog[uid_str][skill] = {"last": lesson_idx, "ts": datetime.utcnow().isoformat()}
    save_json(PROGRESS_PATH, prog)

def clear_progress(uid: int, skill: str):
    prog = load_json(PROGRESS_PATH, {})
    uid_str = str(uid)
    if uid_str in prog and skill in prog[uid_str]:
        del prog[uid_str][skill]
        save_json(PROGRESS_PATH, prog)

# ---------- quizzes ----------
def load_quizzes() -> Dict:
    return load_json(QUIZ_PATH, {})

def get_quiz(skill: str, lesson_idx: int) -> Dict | None:
    all_q = load_quizzes()
    return all_q.get(skill, {}).get(str(lesson_idx))

def save_quiz(skill: str, lesson_idx: int, question: str, options: List[str], correct: int):
    all_q = load_quizzes()
    if skill not in all_q:
        all_q[skill] = {}
    all_q[skill][str(lesson_idx)] = {
        "q": question,
        "o": options,
        "a": correct
    }
    save_json(QUIZ_PATH, all_q)

    # ---------- skill intro (image + caption) ----------
def get_skill_intro(skill: str) -> tuple[str | None, str | None]:
    """
    Returns (caption, thumb_path) for a skill.
    Reads intro.txt and intro.jpg/png from the skill folder.
    The thumbnail is downloaded to a temp file; caller should delete it.
    """
    folder_id = SKILL_ROOT.get(skill)
    if not folder_id:
        return None, None

    files = [f for f in _files_in_folder(folder_id)
         if f["name"].lower() not in {"intro.txt", "intro.jpg", "intro.jpeg", "intro.png"}]    
    caption = None
    thumb_path = None
        

    # 1) look for intro.txt
    txt_file = next((f for f in files if f["name"].lower() == "intro.txt"), None)
    if txt_file:
        try:
            from utils import _drive_service   # reuse the same service
            data = _drive_service().files().get_media(fileId=txt_file["id"]).execute()
            caption = data.decode("utf-8", errors="ignore").strip()
        except Exception:
            pass

    # 2) look for intro image
    for ext in ("jpg", "jpeg", "png"):
        img_file = next((f for f in files if f["name"].lower() == f"intro.{ext}"), None)
        if img_file:
            try:
                request = _drive_service().files().get_media(fileId=img_file["id"])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)

                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
                tmp.write(fh.read())
                tmp.close()
                thumb_path = tmp.name
            except Exception:
                pass
            break

    return caption, thumb_path
def fetch_skill_intro(skill: str) -> tuple[str | None, str | None]:
    folder_id = SKILL_ROOT.get(skill)
    logger.info("fetch_skill_intro: skill=%s folder_id=%s", skill, folder_id)
    if not folder_id:
        return None, None

    files = _files_in_folder(folder_id)
    logger.info("Files in folder: %s", [f["name"] for f in files])

    caption = None
    thumb_path = None

    # --- intro.txt ---
    txt = next((f for f in files if f["name"].lower() == "intro.txt"), None)
    if txt:
        try:
            data = _drive_service().files().get_media(fileId=txt["id"]).execute()
            caption = data.decode("utf-8", errors="ignore").strip()
            logger.info("Found intro.txt, caption=%s", caption[:50])
        except Exception as e:
            logger.warning("intro.txt read failed: %s", e)

    # --- intro image ---
    for ext in ("jpg", "jpeg", "png"):
        img = next((f for f in files if f["name"].lower() == f"intro.{ext}"), None)
        if img:
            try:
                request = _drive_service().files().get_media(fileId=img["id"])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)

                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
                tmp.write(fh.read())
                tmp.close()
                thumb_path = tmp.name
                logger.info("Found intro image: %s", thumb_path)
            except Exception as e:
                logger.warning("intro image download failed: %s", e)
            break

    logger.info("Returning caption=%s thumb=%s", caption, thumb_path)
    return caption, thumb_path