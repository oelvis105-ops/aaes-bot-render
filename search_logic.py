import difflib
from re import match
from utils import search_drive

def fuzzy_match(query, possibilities):
    match = difflib.get_close_matches(query, possibilities, n=1, cutoff=0.5)
    if match:
        return match[0]
    return None

def perform_fuzzy_search(term):
    possibilities = search_drive("list_only")
    if not possibilities:
        return "No materials found."

    corrected = fuzzy_match(term, possibilities)

    if corrected:
        if corrected.lower() != term.lower():
            msg = "Showing results for " + corrected + "\n"
        else:
            msg = ""
        results = search_drive(corrected)
        return msg + results

    return "No close matches found. Try another keyword."
