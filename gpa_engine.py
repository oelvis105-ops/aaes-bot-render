import re
from typing import List, Tuple

GRADE_MAP = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}

def mark_to_grade(mark: int) -> str:
    """Convert 0-100 mark to letter grade."""
    if mark >= 70:
        return "A"
    elif mark >= 60:
        return "B"
    elif mark >= 50:
        return "C"
    elif mark >= 40:
        return "D"
    return "F"

def parse_line(line: str) -> Tuple[str, str, int]:
    """
    Accepts lines like:
    Chemistry, 85, 3
    Chemistry, A, 3
    Returns (course, grade_letter, credits)
    """
    parts = [p.strip() for p in re.split(r"[,|\t]", line) if p.strip()]
    if len(parts) < 3:
        raise ValueError("Need at least 3 columns: course, grade/mark, credits")
    course, grade_or_mark, credits = parts[0], parts[1], parts[2]
    try:
        credits = int(credits)
    except ValueError:
        raise ValueError("Credits must be an integer")
    if grade_or_mark.upper() in GRADE_MAP:
        grade = grade_or_mark.upper()
    else:
        try:
            mark = int(float(grade_or_mark))
            grade = mark_to_grade(mark)
        except ValueError:
            raise ValueError("Grade must be A-F or 0-100 mark")
    return course, grade, credits

def calculate_gpa(lines: List[str]) -> Tuple[float, int, int]:
    """
    Returns (gpa, total_quality_points, total_credits)
    """
    total_qp = 0
    total_credits = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        _, grade, credits = parse_line(line)
        total_qp += GRADE_MAP[grade] * credits
        total_credits += credits
    gpa = total_qp / total_credits if total_credits else 0.0
    return round(gpa, 2), total_qp, total_credits