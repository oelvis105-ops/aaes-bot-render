import json
import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
ROOT = {"slides": "1DjQGc-ibDQXxMTrSnLJwBij5JOCGqw7U",
        "pastquestions": "1nouwo54jay8vFbyYgtPIBmbn5AwBE0Vo",
        "others": "1jGU77fuh-B5AoiXp12vP9QUCdEQqcaPr",
        "skills": "1i6a1lfKcC_F5Vgqr6zHBYn_zBAhHnSsf"
        }  

# example IDs

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)


def get_children(folder_id):
    try:
        results = drive.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=1000,
            fields="files(id,name,mimeType,webViewLink)"
        ).execute()
        return results.get("files", [])
    except HttpError:
        return []

def go_four_levels_down(root_id,tag):
    out = []
    level1 = get_children(root_id)
    for a in level1:
        if a["mimeType"] != "application/vnd.google-apps.folder":
            continue
        level2 = get_children(a["id"])
        for b in level2:
            if b["mimeType"] != "application/vnd.google-apps.folder":
                continue
            level3 = get_children(b["id"])
            for c in level3:
                if c["mimeType"] != "application/vnd.google-apps.folder":
                    continue
                level4 = get_children(c["id"])
                for d in level4:
                    if d["mimeType"] != "application/vnd.google-apps.folder":
                        continue

                    out.append({
                        "id': d["id"],
                        "name": d["name"]
                        "folder":c["name"]
                        "path": a["name"] + "/" + b["name"] + "/" + c["name"] + "/" + d["name"]
                        "link": d.get("webViewLink","")
                        "type": tag
                    })
                  
    return out

def clean_text(name):
    # normalize for easier search
    return (
        name.lower()
        .replace("(", " ")
        .replace(")", " ")
        .replace("-", " ")
        .replace("_", " ")
        .replace("/", " ")
    )


def build_universal_index():
    """Builds the single JSON file the bot expects."""
    index = []
    for tag, folder_id in ROOT.items():
        files = list_all_files_recursive(folder_id)   # reuse your existing helper
        for f in files:
            index.append({
                "name": f["name"],
                "link": f["link"],
                "type": tag,          # slides / pastquestions / skills / others
                "level": _guess_level(f["name"]),
                "id": f["id"]
            })

    os.makedirs("data", exist_ok=True)
    with open("data/drive_index.json", "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)
    print(f"✅ Universal index built: {len(index)} files")

def _guess_level(name: str):
    name = name.lower()
    for lvl in ("100","200","300","400"):
        if lvl in name:
            return f"L{lvl}"
    return ""

def list_all_files_recursive(folder_id):
    out = []
    children = list_files(folder_id)
    for item in children:
        if item["mimeType"] == "application/vnd.google-apps.folder":
            out.extend(list_all_files_recursive(item["id"]))
        else:
            out.append({
                "id": item["id"],
                "name": item["name"],
                "link": item.get("webViewLink", f"https://drive.google.com/file/d/{item['id']}/view")
            })
    return out

if __name__ == "__main__":
    build_universal_index()