"""Skill module — the PUBLIC door: run(skills, rawText).

For every skill Affinda extracted: find it in the text, read the sentence, decide
its status (using the precision guard), and build one Enrichment (severity-stamped),
with the proof highlight pointing at the exact cue words we matched.
"""
from __future__ import annotations

from resume_enricher.modules.skill._classify import classify_skill
from resume_enricher.shared.locator import locate
from resume_enricher.shared.models import Enrichment, build_evidence, severity_of


def run(skills, raw_text):
    out = []
    for i, skill in enumerate(skills):
        name = skill.get("name") or ""
        clause, clause_start, span = locate(skill.get("text") or name, raw_text)
        if clause is None:
            status, matched, pos = "plain", None, None   # couldn't find it -> no signal
        else:
            status, matched, pos = classify_skill(clause, name)
        out.append(
            Enrichment(
                entryIndex=i,
                entity=name,
                status=status,
                confidence="high" if span else "low",
                severity=severity_of("skill", status),
                evidence=build_evidence(name, matched, pos, clause_start, span),
            ).to_dict()
        )
    return out
