# drive_search.py  –  fixed to return list always
from typing import List, Dict, Optional
import os
import json
from rapidfuzz import process, fuzz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ---------- config ----------
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SA_PATH", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]  # fixed space
FOLDER_MIME = "application/vnd.google-apps.folder"

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive = build("drive", "v3", credentials=creds)

INDEX_PATH = "data/drive_index.json"
FUZZY_SCORE_MIN = 60
MAX_RESULTS = 10

# ---------- helpers ----------
def _ensure_index():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, "w") as f:
            json.dump([], f)

def load_index() -> List[Dict]:
    _ensure_index()
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def _normalize_level(level_raw: Optional[str]) -> Optional[str]:
    if not level_raw:
        return None
    s = level_raw.lower()
    for num, label in [("100", "L100"), ("200", "L200"), ("300", "L300"), ("400", "L400")]:
        if num in s or f"l{num}" in s:
            return label
    return None

def _filter_by_mode(items: List[Dict], mode: Optional[str]) -> List[Dict]:
    if not mode or mode == "all":
        return items
    key = mode.lower()
    out = []
    for it in items:
        t = (it.get("type") or "").lower()
        if key == "slides" and "slide" in t:
            out.append(it)
        elif key in ("pastq", "past", "past questions") and ("past" in t or "question" in t):
            out.append(it)
        elif key == "skill" and "skill" in t:
            out.append(it)
        elif key == "other" and t not in ("slides", "pastq", "skill"):
            out.append(it)
    return out

def _filter_by_level(items: List[Dict], level: Optional[str]) -> List[Dict]:
    lv = _normalize_level(level)
    if not lv:
        return items
    return [it for it in items if (it.get("level") or "").upper() == lv]

def _exact_and_substring_search(term: str, items: List[Dict]) -> List[Dict]:
    term_l = term.lower().strip()
    matches = []
    for it in items:
        name = (it.get("name") or "").lower()
        if term_l in name:
            matches.append((100, it))
            continue
        parts = [p.strip() for p in term_l.replace("-", " ").split()]
        if any(p in name for p in parts if len(p) >= 2):
            matches.append((60, it))
    scored = {}
    for score, item in matches:
        k = item.get("link") or item.get("name")
        if k not in scored or scored[k][0] < score:
            scored[k] = (score, item)
    return [v[1] for v in sorted(scored.values(), key=lambda x: x[0], reverse=True)]

def _fuzzy_search(term: str, items: List[Dict], limit: int = MAX_RESULTS) -> List[Dict]:
    names = [it.get("name", "") for it in items]
    if not names:
        return []
    raw = process.extract(term, names, scorer=fuzz.WRatio, limit=limit)
    out = []
    for match_name, score, idx in raw:
        if score >= FUZZY_SCORE_MIN:
            out.append(items[idx])
    seen = set()
    unique = []
    for it in out:
        key = it.get("link") or it.get("name")
        if key not in seen:
            seen.add(key)
            unique.append(it)
    return unique

# ---------- NEW folder-first helpers ----------
def _find_folder_id(query: str) -> Optional[str]:
    """Exact or fuzzy folder match."""
    q = f"mimeType='{FOLDER_MIME}' and trashed=false"
    res = drive.files().list(q=q, fields="files(id,name)", pageSize=200).execute()
    folders = res.get("files", [])
    if not folders:
        return None
    # exact
    for f in folders:
        if f["name"].lower() == query.lower():
            return f["id"]
    # fuzzy
    names = [f["name"] for f in folders]
    match, score, _ = process.extractOne(query, names, scorer=fuzz.WRatio)
    if score >= FUZZY_SCORE_MIN:
        return next(f["id"] for f in folders if f["name"] == match)
    return None

def _files_in_folder(folder_id: str) -> List[Dict]:
    """Return every non-folder file under folder_id (recursive)."""
    out = []
    page_token = None
    while True:
        res = drive.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,size,webViewLink)",
            pageSize=1000,
            pageToken=page_token
        ).execute()
        for f in res.get("files", []):
            if f["mimeType"] == FOLDER_MIME:
                out.extend(_files_in_folder(f["id"]))
            else:
                out.append({
                    "id": f["id"],
                    "name": f["name"],
                    "link": f.get("webViewLink", f"https://drive.google.com/file/d/{f['id']}/view"),
                    "size": int(f.get("size", 0))
                })
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return out

# ---------- public API ----------
def search_drive(term: str, mode: Optional[str] = None, level: Optional[str] = None) -> List[Dict]:
    """
    1. Try folder match first.
    2. Fallback to legacy file-level search (if index exists).
    3. Always returns List[Dict] (empty list if nothing found).
    """
    folder_id = _find_folder_id(term.strip())
    if folder_id:
        return _files_in_folder(folder_id)

    # ---- fallback: legacy index ----
    idx = load_index()
    if not idx:
        return []

    items = _filter_by_mode(idx, mode)
    items = _filter_by_level(items, level)

    exact = _exact_and_substring_search(term, items)
    if exact:
        return exact[:MAX_RESULTS]

    fuzzy = _fuzzy_search(term, items)
    if fuzzy:
        return fuzzy[:MAX_RESULTS]

    return []