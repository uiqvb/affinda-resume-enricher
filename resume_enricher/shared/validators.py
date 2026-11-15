"""The safety checks.

Two jobs:
  1. Before we start, make sure the resume data coming in isn't broken.
  2. When we're done, make sure we didn't accidentally change the original.

Note: Affinda's data is often sparse — a resume may simply have no skills, or no
education section. That's normal, not an error; it just means "nothing to check
here". We only complain when the data is genuinely the wrong shape.
"""
from __future__ import annotations

import copy

# The three lists we read from a resume.
_ENTITY_KEYS = ("skills", "education", "certifications")


def validate_input(affinda: dict) -> None:
    """Check the incoming resume data is usable before we start.

    If something is genuinely broken, we stop with a clear error. If a section is
    just missing or empty, that's fine — we let it through and do nothing for it.
    (A missing resume text is also fine: we just won't be able to show exact
    positions, so those notes get marked "low" confidence.)
    """
    if not isinstance(affinda, dict):
        raise ValueError("The resume data should be a dictionary, but it isn't.")
    if "data" not in affinda:
        raise ValueError("The resume data is missing its 'data' section.")

    data = affinda["data"]
    if not isinstance(data, dict):
        raise ValueError("The 'data' section should be a dictionary, but it isn't.")

    # If a section exists, it must be a list. Missing or empty is allowed.
    for key in _ENTITY_KEYS:
        if key in data and not isinstance(data[key], list):
            raise ValueError(f"'{key}' should be a list, but it isn't.")


def ensure_untouched(original: dict, current: dict) -> None:
    """Our promise: we never change the original resume.

    We work on a copy. At the end we compare the copy's starting point against
    what we handed back. If they differ, something leaked through by mistake, and
    we stop loudly rather than quietly return changed data.
    """
    if current != original:
        raise AssertionError("We accidentally changed the original resume data — this must never happen.")


def deep_copy(data: dict) -> dict:
    """Make a completely separate copy to work on, so edits can't touch the original.

    "Deep" = it copies everything inside too (the nested lists and dicts), not just
    the outer shell — so editing the copy can never reach back into the original.
    """
    return copy.deepcopy(data)
