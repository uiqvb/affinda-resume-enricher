"""Education cue words — which phrases mean which completion status.

Checked in order, first match wins. "expected" also needs a future year in the
sentence (handled by the status engine).
"""

EDU_RULES = [
    ("in_progress", [r"\bcurrently enrolled\b", r"\bin progress\b", r"\bongoing\b",
                     r"\bpursuing\b", r"\bstudying towards\b", r"\bcandidate for\b",
                     r"\benrolled\b", r"\bABD\b", r"\ball but dissertation\b"]),
    ("expected",    [r"\bexpected\b", r"\banticipated\b", r"\bgraduating\b", r"\bdue\b",
                     r"\bprojected\b"]),
    ("incomplete",  [r"\bdiscontinued\b", r"\bincomplete\b", r"\bdid not complete\b",
                     r"\bleft before finishing\b", r"\bunfinished\b", r"\bpartial\b",
                     r"\bdropped out\b", r"\bwithdr(ew|awn)\b"]),
    ("deferred",    [r"\bdeferred\b", r"\bon (academic )?leave\b", r"\bstudy break\b",
                     r"\benrol(l)?ment (suspended|paused)\b", r"\bintermission\b"]),
    ("not_awarded", [r"\bnot awarded\b", r"\bno degree (conferred|awarded)\b",
                     r"\brequirements not met\b", r"\bexams not passed\b"]),
    ("completed",   [r"\bgraduated\b", r"\bconferred\b", r"\bawarded\b", r"\bcompleted\b",
                     r"\bearned\b"]),
]
# nothing matches -> "unknown" (still emitted, severity "info")
