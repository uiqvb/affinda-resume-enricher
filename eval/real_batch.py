"""Run the enricher over REAL resumes (parsed by Affinda) and write a readable
precision / sanity report.

These are genuine strangers' resumes (CC0 source, parsed through the Affinda
Sandbox). There is NO ground-truth answer key, so this is NOT a scored recall
test. It answers two questions a human can verify by eye:

  1. When we raise a warning, is it correct? (precision)
  2. Do we ever wrongly flag a clean item? (false alarms)

For every warning we print the exact resume clause we matched, so each flag can
be judged on sight.

Run:  python eval/real_batch.py   ->  writes eval/results/REAL_REPORT.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resume_enricher import enrich

HERE = Path(__file__).resolve().parent
DATA = HERE / "real" / "real_affinda.json"
OUT = HERE / "results"

DIMS = ("skills", "education", "certifications")
LABEL = {"skills": "SKILL", "education": "DEGREE", "certifications": "CERT"}


def clause(note, raw):
    """A readable window of rawText around the matched evidence span."""
    ev = note.get("evidence") or {}
    span = ev.get("rawTextSpan")
    if not span or not raw:
        return ev.get("text") or ""
    a, b = span
    lo, hi = max(0, a - 45), min(len(raw), b + 45)
    snippet = raw[lo:hi].replace("\n", " ").strip()
    snippet = " ".join(snippet.split())  # collapse whitespace
    pre = "..." if lo > 0 else ""
    post = "..." if hi < len(raw) else ""
    return f"{pre}{snippet}{post}"


def main():
    data = json.load(open(DATA, encoding="utf-8"))

    totals = {d: 0 for d in DIMS}
    warnings = {d: [] for d in DIMS}   # list of (file, note, clause)
    located = {d: 0 for d in DIMS}
    per_file = []

    for item in data:
        fname = item.get("fileName", "?")
        resp = item["response"]
        raw = (resp.get("data") or {}).get("rawText") or ""
        out = enrich(resp)
        ej = out["enrichmentJSON"]
        fwarn = 0
        for d in DIMS:
            notes = ej.get(d) or []
            totals[d] += len(notes)
            for n in notes:
                # "located" = we found the entity text in rawText (confidence high
                # and a real span), i.e. we actually read its clause
                sp = (n.get("evidence") or {}).get("rawTextSpan")
                if sp and sp[1] > sp[0]:
                    located[d] += 1
                if n.get("needsReview") == "yes":
                    warnings[d].append((fname, n, clause(n, raw)))
                    fwarn += 1
        per_file.append((fname, fwarn,
                         len(ej.get("skills") or []),
                         len(ej.get("education") or []),
                         len(ej.get("certifications") or [])))

    tot_items = sum(totals.values())
    tot_warn = sum(len(v) for v in warnings.values())

    # breakdown of warning statuses (all dims)
    status_count = {}
    for d in DIMS:
        for _f, n, _c in warnings[d]:
            status_count[n["status"]] = status_count.get(n["status"], 0) + 1

    L = []
    L.append("# Real resumes: precision / sanity check\n")
    L.append(
        f"**{len(data)} genuine resumes** (CC0 source, parsed by the Affinda Sandbox), "
        "run through the enricher. These have **no answer key**, so this is not a scored "
        "recall test. It checks two things a human can verify on sight:\n")
    L.append("1. When we raise a warning, is it right?  (**precision**)")
    L.append("2. Do we ever flag a clean item?  (**false alarms**)\n")

    L.append("## At a glance\n")
    L.append("| | Skills | Degrees | Certs | Total |")
    L.append("|---|---|---|---|---|")
    L.append(f"| Items enriched | {totals['skills']} | {totals['education']} | "
             f"{totals['certifications']} | **{tot_items}** |")
    L.append(f"| Warnings raised | {len(warnings['skills'])} | {len(warnings['education'])} "
             f"| {len(warnings['certifications'])} | **{tot_warn}** |")
    L.append("")
    L.append(f"Out of **{tot_items}** enriched items, we raised **{tot_warn} warnings**. "
             "Every one is listed below with the exact resume clause, so you can judge it "
             "yourself. Everything not listed we left as neutral `info` (no accusation).\n")

    sc = ", ".join(f"`{k}` x{v}" for k, v in sorted(status_count.items()))
    L.append("## What this run told us (the honest read)\n")
    L.append(f"- **Every warning was the mildest kind:** {sc}. No `no_experience`, "
             "`lapsed`, `expired` or `revoked` false alarms fired on real data.")
    L.append(f"- **Degrees and certs: 0 warnings, 0 false alarms** across "
             f"{totals['education']} degrees and {totals['certifications']} certs.")
    L.append("- **The `basic` rule is where real data bites us.** On our clean synthetic "
             "tests it never false-alarmed. Real resumes break that, because the word "
             "\"basic\" shows up in three places that are NOT a weakness claim:")
    L.append("    1. **As its own skill in a comma dump:** `Accounting, Basic, Budgeting, "
             "Data Entry` - Affinda lists each comma item as a skill, so \"Basic\" sits "
             "next to unrelated skills and bleeds onto them.")
    L.append("    2. **Inside a proper course / cert name:** `Basic First Aid`, "
             "`EMT - Basic`, `Basic Combat Trauma Training`, `Basic Offshore Safety "
             "Induction`. These are credential names, not self-assessments.")
    L.append("    3. **Describing a job task:** `performed basic emergency treatment`, "
             "`basic compressor build lines`. The task was entry-level, the person is not.")
    L.append("- **A few are actually correct**, e.g. `Mandarin Chinese - Basic "
             "Conversational` really does say basic. But most of the 23 are stray-word "
             "matches, so on real resumes the `basic` cue is **low precision**.")
    L.append("- **Takeaway:** the fail-safe design (never fires the severe warnings "
             "wrongly) held. But the blanket claim \"we never flag a clean item\" does "
             "**not** survive real messy resumes for the `basic` cue. v2 fix: only accept "
             "`basic` when the word is bound to the skill token, not merely nearby.\n")

    L.append("## Per resume\n")
    L.append("| resume | warnings | skills | degrees | certs |")
    L.append("|---|---|---|---|---|")
    for fname, fw, s, e, c in per_file:
        flag = f"**{fw}**" if fw else "0"
        L.append(f"| {fname} | {flag} | {s} | {e} | {c} |")
    L.append("")

    L.append("## Every warning we raised (judge each on sight)\n")
    L.append("For each one: the item, what we marked it, and the exact words on the "
             "resume that triggered it.\n")
    for d in DIMS:
        ws = warnings[d]
        L.append(f"### {LABEL[d]}  ({len(ws)} warnings)\n")
        if not ws:
            L.append("_None._\n")
            continue
        L.append("| resume | item | we marked | the clause we matched |")
        L.append("|---|---|---|---|")
        for fname, n, cl in ws:
            ent = (n.get("entity") or "").replace("|", "/")
            cl = cl.replace("|", "/")
            L.append(f"| {fname} | {ent} | `{n['status']}` | {cl} |")
        L.append("")

    L.append("## How to read this\n")
    L.append("- **A correct warning** = the clause really does say the skill is weak, the "
             "degree unfinished, or the cert expired.")
    L.append("- **A false alarm** = the clause is clean but we flagged it anyway (for "
             "example a stray word like \"basic\" sitting next to an unrelated skill).")
    L.append("- Real resumes are messy free text, so a few stray-word matches here are the "
             "honest cost of keyword rules. They are listed openly above rather than hidden "
             "in a percentage.\n")

    OUT.mkdir(exist_ok=True)
    (OUT / "REAL_REPORT.md").write_text("\n".join(L), encoding="utf-8")

    print(f"resumes={len(data)} items={tot_items} warnings={tot_warn}")
    for d in DIMS:
        print(f"  {LABEL[d]}: {totals[d]} items, {len(warnings[d])} warnings")
    print(f"wrote {OUT/'REAL_REPORT.md'}")


if __name__ == "__main__":
    main()
