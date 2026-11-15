"""The finder — the "brain" that locates an item in the resume text.

Give it a word (like "SQL") and the full resume text. It finds the word, hands
back the SENTENCE around it (for the rules to read) and the EXACT spot (for the
highlight). If it can't find the word, it says so honestly.

It leans on the text helpers in `matching.py`.
"""
from __future__ import annotations

# The four helpers below all come from matching.py (the "hands" this brain uses):
#   normalize           - clean the small search word
#   normalize_mapped    - clean the big resume text + give the index map
#   exact_token_find    - find a whole word
#   fuzzy_spaceless_find- backup find for words split by spaces ("S Q L")
from resume_enricher.shared.matching import (
    exact_token_find,
    fuzzy_spaceless_find,
    normalize,
    normalize_mapped,
)

# Characters that end a sentence / clause — we widen out to these.
# DEFAULT (used for skills): dashes and bullets ARE boundaries, because résumés
# list skills like "Git — Linux — Agile" and each skill must stay separate.
_BOUNDARIES = set(".;!?\n|—–•·")   # . ; ! ? newline | — – • ·
# STATUS set (used for education & certification): dashes and bullets are NOT
# boundaries, because those entries put the qualifier AFTER a dash, e.g.
# "CISSP — expired 2022" or "BSc … — currently enrolled". If we stopped at the
# dash we'd never see the status word. We still stop at real sentence ends.
STATUS_BOUNDARIES = set(".;!?\n|")
_MAX_WINDOW = 120                                      # never grab more than ~120 chars each side


def clause_around(
    text: str, start: int, end: int, boundaries: set[str] = _BOUNDARIES
) -> tuple[str, int]:
    """Grow left and right from the found word until a sentence boundary (or the
    ~120-char limit), and return that one sentence.

    Gives back TWO things:
      - the sentence itself, trimmed of spare spaces at the ends
      - where that trimmed sentence BEGINS in the original text (its start position)

    We hand back the start position so the caller can later turn "position 8 inside
    the sentence" into "position 8 in the whole resume" — that's what keeps a cue's
    highlight exact.
    """
    left = start
    while left > 0 and text[left - 1] not in boundaries and (start - left) < _MAX_WINDOW:
        left -= 1
    right = end
    while right < len(text) and text[right] not in boundaries and (right - end) < _MAX_WINDOW:
        right += 1
    window = text[left:right]
    lead = len(window) - len(window.lstrip())   # spaces we trim off the FRONT
    return window.strip(), left + lead          # start shifts right by the trimmed spaces


def locate(
    entity_text: str, raw_text: str, boundaries: set[str] = _BOUNDARIES
) -> tuple[str | None, int | None, tuple[int, int] | None]:
    """Find `entity_text` inside `raw_text`.

    Returns (clause, clauseStart, span):
      - clause      = the sentence around the word (what the rules will scan)
      - clauseStart = where that sentence begins in the ORIGINAL raw_text
      - span        = (start, end) character positions of the WORD in the original text
    Returns (None, None, None) when the word can't be found — the caller then stays
    safe (status stays plain/unknown, confidence low, no highlight).
    """
    needle = normalize(entity_text or "")            # matching.py: clean the search word
    if not needle:
        return None, None, None

    clean, index_map = normalize_mapped(raw_text or "")  # matching.py: clean text + index map

    # 1) exact whole-word match on the cleaned text
    pos = exact_token_find(clean, needle)            # matching.py: whole-word find
    if pos != -1:
        c_start, c_end = pos, pos + len(needle) - 1
    else:
        # 2) fallback for words broken up by spaces/line breaks ("S Q L")
        found = fuzzy_spaceless_find(clean, needle)  # matching.py: spaceless backup find
        if found is None:
            return None, None, None
        c_start, c_end = found

    # translate the cleaned-text positions back to the ORIGINAL text
    start = index_map[c_start]
    end = index_map[c_end] + 1
    clause, clause_start = clause_around(raw_text, start, end, boundaries)
    return clause, clause_start, (start, end)
