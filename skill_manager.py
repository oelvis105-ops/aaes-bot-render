import os
import json

PATH = "data/skills"
def init_skills():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PATH):
        os.makedirs(PATH)
# Default starter skills
defaults = {
    "arduino": "Intro to Arduino.\n\nStart with digital pins, analog readings, and simple circuits.",
    "python": "Intro to Python.\n\nCovers variables, loops, functions, and simple scripts.",
    "3dmodeling": "Intro to 3D Modeling.\n\nLearn basic CAD navigation, sketches, and extrusions.",
    "autocad": "AutoCAD Basics.\n\nCoordinates, lines, constraints, and layering.",
    "ai_basics": "AI Basics.\n\nCovers prompts, text generation, and problem solving.",
}

for name, content in defaults.items():
    file = f"{PATH}/{name}.txt"
    if not os.path.exists(file):
        with open(file, "w") as f:
            f.write(content)


def available_skills():
    init_skills()
    skills = []
    for file in os.listdir(PATH):
        if file.endswith(".txt"):
            skills.append(file.replace(".txt", ""))
    return skills

def load_skill(name):
    init_skills()
    file = f"{PATH}/{name}.txt"
    if os.path.exists(file):
        with open(file, "r") as f:
            return f.read().strip()
        
def save_skill(name, content):
    init_skills()
    file = f"{PATH}/{name}.txt"
    with open(file, "w") as f:
        f.write(content.strip())
    return True
