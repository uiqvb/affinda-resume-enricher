"""The skill if/else core: decide a skill's status from the sentence around it.

THE PRECISION GUARD. One resume sentence often lists several skills with different
strengths: "no experience with SQL, but expert in Python". If we read the whole
sentence for SQL we'd wrongly see "expert" and call SQL strong. So we don't read the
whole sentence — we read only the small PIECE that actually belongs to this skill.

How we cut the sentence into pieces: we split it at "walls". A wall is either
punctuation (a comma, semicolon, colon or pipe) or a joining word like "and", "but",
"while". These are the natural fences between one skill's description and the next.
We then keep only the piece that contains THIS skill, and judge its status from that
piece alone.

We also report WHERE the matched cue sits, so the proof highlight can be exact.
(Typo-tolerant "fuzzy" cue matching is a deliberately-deferred later upgrade.)
"""
from __future__ import annotations

import re

from resume_enricher.modules.skill._rules import SKILL_RULES

# A "wall" between two skills' descriptions: punctuation, or a joining word.
_WALL = re.compile(r"[;,:|]|\b(?:and|but|however|whereas|while|though|also|plus)\b", re.IGNORECASE)


def _pieces(clause: str) -> list[tuple[int, str]]:
    """Cut the sentence at every wall. Return each piece as (start_position, text).

    The start_position is where that piece begins inside the sentence — we keep it so
    a cue found in the piece can be traced back to its spot in the whole sentence.
    """
    out: list[tuple[int, str]] = []
    last = 0
    for wall in _WALL.finditer(clause):
        if wall.start() > last:
            out.append((last, clause[last:wall.start()]))
        last = wall.end()
    if last < len(clause):
        out.append((last, clause[last:]))
    return out


def _piece_around(clause: str, skill_name: str) -> tuple[int, str]:
    """Return the (start_position, text) of the one piece that holds this skill.

    Falls back to the whole sentence (start 0) if we can't isolate a single piece —
    better to read a bit too much than to lose the skill entirely.
    """
    low = (skill_name or "").lower()
    for start, text in _pieces(clause):
        if low and low in text.lower():
            return start, text
    return 0, clause


def classify_skill(clause: str, skill_name: str) -> tuple[str, str | None, int | None]:
    """Decide the skill's status from its own piece of the sentence.

    Returns three things:
      - status   : the strength we settled on (e.g. "no_experience", "strong", "plain")
      - matched  : the exact cue words we matched, or None if nothing matched
      - position : where those cue words start inside the whole sentence, or None

    Rules are tried in priority order (worst/strongest signal first); first hit wins.
    If no cue matches, the skill is "plain" (still reported, needsReview False).
    """
    piece_start, piece = _piece_around(clause, skill_name)
    for status, patterns in SKILL_RULES:
        for pattern in patterns:
            match = re.search(pattern, piece, re.IGNORECASE)
            if match:
                return status, match.group(0), piece_start + match.start()
    return "plain", None, None
