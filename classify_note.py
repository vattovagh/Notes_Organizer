"""
Classify note text into a broad subject category.
Uses keyword scoring; works offline with no API keys.
"""

import re
from typing import Optional

# Broad subject categories and representative keywords (case-insensitive).
# Add or remove categories and keywords as needed.
SUBJECT_KEYWORDS = {
    "Mathematics": [
        "equation", "algebra", "calculus", "integral", "derivative", "function",
        "theorem", "proof", "geometry", "trigonometry", "matrix", "vector",
        "solve", "graph", "formula", "fraction", "polynomial", "quadratic",
        "probability", "statistics", "sum", "limit", "angle", "triangle",
    ],
    "Science": [
        "atom", "molecule", "cell", "biology", "chemistry", "physics",
        "experiment", "hypothesis", "reaction", "organism", "evolution",
        "energy", "force", "mass", "velocity", "periodic", "element",
        "lab", "scientific", "theory", "genetic", "DNA", "protein",
    ],
    "Computer Science": [
        "programming", "code", "algorithm", "function", "variable", "class",
        "object", "java", "python", "loop", "array", "string", "boolean",
        "software", "database", "API", "syntax", "debug", "compile",
        "object-oriented", "instance", "method", "constructor", "inheritance",
    ],
    "History": [
        "war", "century", "empire", "revolution", "ancient", "medieval",
        "civilization", "battle", "king", "queen", "colony", "independence",
        "constitution", "treaty", "era", "dynasty", "archaeology",
    ],
    "Literature": [
        "novel", "poem", "character", "theme", "plot", "author", "chapter",
        "metaphor", "symbolism", "narrator", "genre", "literary", "quote",
        "essay", "story", "fiction", "poetry", "drama", "protagonist",
    ],
    "Art": [
        "painting", "drawing", "sketch", "canvas", "perspective", "composition",
        "color", "brush", "portrait", "landscape", "sculpture", "gallery",
        "artist", "medium", "technique", "artwork", "exhibition",
    ],
    "Music": [
        "chord", "scale", "rhythm", "melody", "key", "tempo", "note",
        "instrument", "piano", "guitar", "composition", "harmony", "beat",
        "major", "minor", "octave", "staff", "clef", "notation",
    ],
    "Philosophy": [
        "ethics", "logic", "argument", "premise", "conclusion", "philosophy",
        "existential", "moral", "reason", "belief", "socrates", "plato",
        "consciousness", "truth", "knowledge", "metaphysics",
    ],
}


# Whole-word patterns (optional plural), so "sum" doesn't match "summary".
# Keywords are lowercased because the text is lowercased before matching.
_KEYWORD_PATTERNS = {
    category: [re.compile(r"\b" + re.escape(kw.lower()) + r"(?:s|es)?\b") for kw in keywords]
    for category, keywords in SUBJECT_KEYWORDS.items()
}


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace for matching."""
    if not text or not text.strip():
        return ""
    return re.sub(r"\s+", " ", text.lower().strip())


def classify_text(text: str) -> str:
    """
    Classify note text into one broad subject category.
    Returns the category name with the highest keyword score, or "Other" if none match.
    """
    normalized = _normalize(text)
    if not normalized:
        return "Other"

    best_category = "Other"
    best_score = 0

    for category, patterns in _KEYWORD_PATTERNS.items():
        score = sum(1 for pattern in patterns if pattern.search(normalized))
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


def classify_and_report(text: str, note_name: Optional[str] = None) -> tuple[str, str]:
    """
    Classify text and return (category, report_line).
    Useful for printing or logging.
    """
    category = classify_text(text)
    label = note_name or "Note"
    report = f"{label}: {category}"
    return category, report


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python classify_note.py <text_file>  OR  echo 'text' | python classify_note.py -")
        sys.exit(1)
    path = sys.argv[1]
    if path == "-":
        text = sys.stdin.read()
        name = "stdin"
    else:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        name = path
    category, report = classify_and_report(text, name)
    print(report)
