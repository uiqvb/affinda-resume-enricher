"""The blank forms our tool fills in.

Before we judge anything, we decide what our notes should look like. This file
holds those shapes (the "entity models" — the shape of our data). Everything else
in the project fills in these same forms, so skills, education and certifications
all speak the same language.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Evidence:
    """The proof behind an enrichment. Just two things."""

    text: str                                   # the exact words we found, e.g. "No experience with SQL"
    rawTextSpan: tuple[int, int] | None = None  # where those words sit in the resume: a start and end
    #                                             position. None means we couldn't pin down the spot.


def build_evidence(
    entity_name: str,
    matched: str | None,
    match_pos: int | None,
    clause_start: int | None,
    entity_span: tuple[int, int] | None,
) -> "Evidence":
    """Make the proof for one enrichment, with its TEXT and its HIGHLIGHT lined up.

    This is the rule we keep everywhere: evidence.text and evidence.rawTextSpan must
    describe the SAME thing. Two cases:

      1. We found cue words (e.g. "no experience"): the proof is those words, and the
         highlight points at THEM. We work out where they sit in the whole resume by
         adding their spot inside the sentence (`match_pos`) to where the sentence
         starts (`clause_start`).
      2. No cue words (status is "plain"/"unknown"): the proof is just the item's own
         name, and the highlight points at the ITEM (`entity_span`).
    """
    if matched is not None and match_pos is not None and clause_start is not None:
        span = (clause_start + match_pos, clause_start + match_pos + len(matched))
        return Evidence(matched, span)
    return Evidence(entity_name, entity_span)


@dataclass
class Enrichment:
    """One piece of enrichment — the metadata we add about one single item
    (one skill, one degree, or one certificate). We make ONE of these for EVERY
    item, so our output is a complete mirror of Affinda's list with added context."""

    entryIndex: int        # which original item this is about — its position in Affinda's list (0 = first)
    entity: str            # the item's name, copied so a human can double-check (e.g. "SQL")
    status: str            # the metadata we discovered (e.g. "no_experience", "expired", "strong", "plain")
    confidence: str        # how sure we are of the status: "high" or "low"
    needsReview: str       # "yes" = a human should glance at this; "no" = nothing to flag — for easy filtering
    evidence: Evidence     # the proof (see above)

    def to_dict(self) -> dict:
        """Turn this enrichment into a plain dictionary so it can be saved as JSON."""
        return asdict(self)


@dataclass
class EnrichedJSON:
    """The final package we hand back: the original, plus our enrichments."""

    originalJSON: dict     # Affinda's original response — copied, and never changed
    enrichmentJSON: dict   # a JSON of enrichments (everything WE add): which checks ran, plus the
    #                        lists of skill / education / certificate Enrichment pieces and a summary.


# --- The full status menu + whether each status needs a human glance --------
# We are a full ENRICHER: we record a status for EVERY item, not just the bad ones.
# This one table does two jobs:
#   1. its KEYS are the complete list of allowed statuses (the official menu) —
#      a status not listed here is a typo/bug, and needs_review_of() fails loudly;
#   2. its VALUES tag each status "yes" (a human should glance at it) or "no"
#      (nothing to flag: fine, or just neutral context), so the customer can filter.
STATUS_NEEDS_REVIEW: dict[str, dict[str, str]] = {
    "skill": {
        "no_experience": "yes", "learning": "yes", "lapsed": "yes", "basic": "yes",
        "intermediate": "no", "strong": "no", "plain": "no",
    },
    "education": {
        "in_progress": "yes", "expected": "yes", "incomplete": "yes",
        "deferred": "yes", "not_awarded": "yes",
        "completed": "no", "unknown": "no",
    },
    "certification": {
        "expired": "yes", "revoked": "yes", "suspended": "yes", "pending": "yes",
        "active": "no", "unknown": "no",
    },
}


def needs_review_of(kind: str, status: str) -> str:
    """Look up whether a status needs a human glance: "yes" or "no".

    Fails loudly if the status isn't on the official menu for that kind — that
    means a typo somewhere, which we want to catch, not silently ignore.
    """
    try:
        return STATUS_NEEDS_REVIEW[kind][status]
    except KeyError:
        raise ValueError(f"unknown {kind} status '{status}' — not on the allowed menu")
