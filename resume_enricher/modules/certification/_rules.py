"""Certification cue words — which phrases mean which validity status.

Checked in order, first match wins.
"""

CERT_RULES = [
    ("expired",   [r"\bexpired\b", r"\blapsed\b", r"\bno longer valid\b", r"\bout of date\b"]),
    ("revoked",   [r"\brevoked\b", r"\brescinded\b", r"\bwithdrawn by (the )?issuer\b",
                   r"\bstruck off\b", r"\bcancelled by\b"]),
    ("suspended", [r"\bsuspended\b", r"\bunder suspension\b",
                   r"\btemporarily (inactive|withdrawn)\b"]),
    ("pending",   [r"\bpending\b", r"\bscheduled\b", r"\bawaiting\b", r"\bcandidate\b",
                   r"\bregistered for\b", r"\bsitting\b", r"\bdid not pass\b",
                   r"\bunsuccessful\b", r"\bfailed\b"]),
    ("active",    [r"\bactive\b", r"\bcurrent\b", r"\bin good standing\b", r"\bvalid\b",
                   r"\brenewed\b", r"\brecertified\b"]),
]
# nothing matches -> "unknown" (still emitted, needsReview False)
