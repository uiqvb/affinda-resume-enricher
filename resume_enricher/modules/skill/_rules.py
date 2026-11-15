"""Skill cue words — which phrases mean which skill status.

Checked in THIS order (first match wins), strongest/worst signal first, so a clear
negation beats a weak cue. Matched against the piece of sentence around the skill.
(v0 uses plain patterns; typo-tolerant "fuzzy" matching is a later upgrade.)
"""

SKILL_RULES = [
    ("no_experience", [r"\bno\s+(experience|exposure|background|knowledge)\b",
                       r"\bwithout\s+(any\s+)?\w*\s*(experience|background)\b",
                       r"\bnot\s+(proficient|experienced|familiar)\b",
                       r"\bnever\s+(used|worked with|touched)\b",
                       r":\s*none\b"]),
    ("learning",      [r"\b(currently\s+)?(learning|studying|teaching myself)\b",
                       r"\binterested in\b", r"\bkeen to learn\b", r"\baspir(e|ing)\b"]),
    ("lapsed",        [r"\b(previously|formerly|used to)\b", r"\byears ago\b",
                       r"\bnot in recent years\b", r"\bno longer (use|work)\b"]),
    ("basic",         [r"\bbasic\b", r"\bfamiliar with\b", r"\bsome\b", r"\blimited\b",
                       r"\bbrief\b", r"\bexposure to\b", r"\bbeginner\b", r"\bentry[- ]level\b"]),
    ("intermediate",  [r"\bworking knowledge\b", r"\bhands[- ]on\b", r"\bcomfortable with\b",
                       r"\bmoderate\b", r"\bsolid\b"]),
    ("strong",        [r"\bexpert\b", r"\badvanced\b", r"\bextensive\b", r"\bstrong\b",
                       r"\bproficient\b", r"\bseasoned\b", r"\b\d+\+?\s*years?\b",
                       r"\bdeep (experience|expertise)\b"]),
]
# nothing matches -> "plain" (still emitted, severity "info")
