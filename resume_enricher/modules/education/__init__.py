"""Education module — the PUBLIC door: run(entries, rawText).

A thin wrapper over the shared status engine, handing it the education rules.
"""
from __future__ import annotations

from resume_enricher.modules.education._rules import EDU_RULES
from resume_enricher.shared.status_engine import run_status


def run(entries, raw_text):
    return run_status(entries, raw_text, EDU_RULES, "education")
