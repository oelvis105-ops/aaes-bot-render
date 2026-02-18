import random
from datetime import datetime, timedelta

def generate_timetable(courses: list[dict], study_hours: int = 4) -> str:
    """
    courses: [{"code": "ME 461", "credits": 3}, ...]
    Returns a Markdown-formatted weekly timetable
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = [f"{h}:00" for h in range(8, 8 + study_hours)]
    timetable = "📅 *Your Weekly Study Timetable*\n\n"

    for day in days:
        timetable += f"*{day}*\n"
        day_courses = random.sample(courses, min(len(courses), len(slots)))
        for t, course in zip(slots, day_courses):
            timetable += f"  `{t}` → {course['code']} ({course['credits']} cr)\n"
        timetable += "\n"
    return timetable