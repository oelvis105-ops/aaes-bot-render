import json, os, time
from typing import List, Dict

PATH = "data/internship_alerts.json"

def _init():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(PATH):
        with open(PATH, "w") as f:
            json.dump([], f)

def load_alerts() -> List[Dict]:
    _init()
    with open(PATH) as f:
        return json.load(f)

def save_alerts(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)

def add_alert(text: str, posted_by: int) -> bool:
    alerts = load_alerts()
    alerts.append({
        "text": text,
        "ts": int(time.time()),
        "posted_by": posted_by
    })
    save_alerts(alerts)
    return True

def last_n(n: int = 5) -> List[str]:
    alerts = load_alerts()
    return [a["text"] for a in sorted(alerts, key=lambda x: x["ts"], reverse=True)[:n]]