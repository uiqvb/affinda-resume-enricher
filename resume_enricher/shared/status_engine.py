"""The shared status engine — used by BOTH education and certification.

Education and certification ask the same question: "what is the status of this
item?" So they share one engine here. Each one passes in its own list of cue
rules; this engine finds the item in the resume text, reads the sentence around
it, and picks the FIRST status whose cue words match.

Skills do NOT use this — they have their own classifier (the precision guard).
"""
from __future__ import annotations

import re
from datetime import date

from resume_enricher.shared.locator import STATUS_BOUNDARIES, locate
from resume_enricher.shared.models import Enrichment, build_evidence, severity_of

_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")       # a 4-digit year like 2016 or 2027


def _has_future_year(clause: str, current_year: int) -> bool:
    """True if the sentence mentions a year later than this year (for 'expected')."""
    return any(int(y) > current_year for y in _YEAR.findall(clause))


def classify_status(clause, entry, rules, current_year):
    """Read the sentence and return (status, matched_words, position).

    Rules are checked in order, first match wins. "expected" is special: it only
    counts if the sentence also has a future year (otherwise we skip it). The
    position is where the matched words start inside the sentence (or None).
    """
    future = _has_future_year(clause, current_year)
    for status, patterns in rules:
        for pattern in patterns:
            match = re.search(pattern, clause, re.IGNORECASE)
            if match:
                if status == "expected" and not future:
                    continue
                return status, match.group(0), match.start()
    return "unknown", None, None                 # no cue matched


def run_status(entries, raw_text, rules, kind):
    """Make ONE Enrichment for every entry (full mirror), each severity-stamped."""
    current_year = date.today().year
    out = []
    for i, entry in enumerate(entries):
        name = entry.get("qualification") or entry.get("name") or ""
        # edu/cert use the wider boundary set so a qualifier after a dash
        # ("CISSP — expired 2022") stays in view.
        clause, clause_start, span = locate(name, raw_text, STATUS_BOUNDARIES)
        if clause is None:
            status, matched, pos = "unknown", None, None   # couldn't find it -> no signal
        else:
            status, matched, pos = classify_status(clause, entry, rules, current_year)
        out.append(
            Enrichment(
                entryIndex=i,
                entity=name,
                status=status,
                confidence="high" if span else "low",
                severity=severity_of(kind, status),
                evidence=build_evidence(name, matched, pos, clause_start, span),
            ).to_dict()
        )
    return out
