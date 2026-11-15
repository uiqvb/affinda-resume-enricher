"""The low-level text helpers — the "hands" of the finder.

Affinda gives us a clean word like "SQL". The important small print ("no
experience with SQL") is hidden in the big blob of résumé text, which is messy:
odd spacing, punctuation, line breaks. These helpers clean that text so we can
find the word, and remember where everything came from so our highlights stay
exact.

The brain that uses these helpers is in `locator.py`.
"""
from __future__ import annotations

import re

_PARENS = re.compile(r"\([^)]*\)")   # e.g. the "(Programming Language)" Affinda tacks on


def normalize_mapped(text: str) -> tuple[str, list[int]]:
    """Clean `text` and remember where every cleaned character came from.

    Cleaning = lowercase everything, and turn every run of spaces/punctuation
    into a SINGLE space (so "S Q L", line breaks and stray punctuation all line
    up).

    Returns two things:
      - the cleaned string
      - an "index map": a list the SAME length as the cleaned string, where
        index_map[i] is the position of that character back in the ORIGINAL
        text. This is what lets us point at the exact original spot later.
    """
    out: list[str] = []
    index_map: list[int] = []
    prev_space = True                       # True so we never start with a space

    for i, ch in enumerate(text):
        if ch.isalnum():                    # a real letter or digit -> keep it
            out.append(ch.lower()[0])       # [0] keeps it to one char, so the map stays 1:1
            index_map.append(i)
            prev_space = False
        elif not prev_space:                # a space or punctuation -> becomes ONE space
            out.append(" ")
            index_map.append(i)
            prev_space = True
        # else: already on a space -> skip it (this is what collapses runs)

    if out and out[-1] == " ":              # drop a trailing space, if any
        out.pop()
        index_map.pop()

    return "".join(out), index_map


def normalize(text: str) -> str:
    """Clean a small search word (the needle). No map needed.

    Reuses `normalize_mapped` and throws the map away. It also drops Affinda's
    parenthetical notes like "(Programming Language)" first, so
    "Python (Programming Language)" becomes just "python".
    """
    return normalize_mapped(_PARENS.sub(" ", text))[0]


def exact_token_find_all(hay: str, needle: str) -> list[int]:
    """Find EVERY whole-word occurrence of `needle` in `hay`.

    Both are already cleaned (single spaces between words). We only accept a
    match that sits between spaces / the ends — so "c" matches a standalone "c",
    never the "c" inside "communication". Returns a list of start positions,
    in reading order (empty if none).
    """
    out: list[int] = []
    if not needle:
        return out

    start = 0
    while True:
        pos = hay.find(needle, start)
        if pos == -1:
            return out
        before = hay[pos - 1] if pos > 0 else " "
        after = hay[pos + len(needle)] if pos + len(needle) < len(hay) else " "
        if before == " " and after == " ":
            out.append(pos)
        start = pos + 1


def exact_token_find(hay: str, needle: str) -> int:
    """The FIRST whole-word occurrence of `needle`, or -1 if there is none."""
    found = exact_token_find_all(hay, needle)
    return found[0] if found else -1


def fuzzy_spaceless_find(hay: str, needle: str) -> tuple[int, int] | None:
    """Backup search for words broken up by spaces / line breaks, e.g. "S Q L".

    We squeeze the spaces out of both and look again — but we only accept a match
    that still sits on WORD BOUNDARIES in `hay`, so "Ada" can't match the "ada"
    buried inside "Canada". Only used for needles of 3+ characters, so short
    tokens like "c" (from "C++") can't match random letters. Returns the
    (start, end) range in `hay`, or None.
    """
    needle_ns = needle.replace(" ", "")
    if len(needle_ns) < 3:
        return None

    # positions of the non-space characters, so we can map back into `hay`
    ns_positions = [j for j, ch in enumerate(hay) if ch != " "]
    hay_ns = "".join(hay[j] for j in ns_positions)

    search_from = 0
    while True:
        p = hay_ns.find(needle_ns, search_from)
        if p == -1:
            return None
        start = ns_positions[p]
        end = ns_positions[p + len(needle_ns) - 1]
        before = hay[start - 1] if start > 0 else " "
        after = hay[end + 1] if end + 1 < len(hay) else " "
        if before == " " and after == " ":     # a real word, not stuck inside one
            return start, end
        search_from = p + 1                     # keep looking past this false hit
