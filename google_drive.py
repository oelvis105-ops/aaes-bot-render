import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive = build("drive", "v3", credentials=creds)


def list_files(folder_id):
    try:
        results = drive.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=1000,
            fields="files(id,name,mimeType,webViewLink)"
        ).execute()
        return results.get("files", [])
    except HttpError:
        return []


def list_all_files_recursive(folder_id):
    out = []
    children = list_files(folder_id)

    for item in children:
        mime = item["mimeType"]
        if mime == "application/vnd.google-apps.folder":
            deeper = list_all_files_recursive(item["id"])
            out.extend(deeper)
        else:
            out.append({
                "id": item["id"],
                "name": item["name"],
                "link": item.get("webViewLink", "")
            })

    return out
