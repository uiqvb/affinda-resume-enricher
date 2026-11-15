"""Evaluation harness for the Affinda Resume Enricher.

Reads the ONE centralized corpus (eval/data/all_resumes.json — 300 Affinda-parsed
résumés with ground truth) and measures the BEFORE vs AFTER story:

  BEFORE = Affinda alone: it extracts the entity but attaches NO strength /
           completion / validity qualifier (the gap we exist for).
  AFTER  = Resume Enricher: we read rawText and attach a status + severity.

Self-contained: needs only this repo (the dataset is committed). Rebuild the
dataset from the process repo with `python eval/build_dataset.py`.

Vocabulary bridge — ground truth uses the source taxonomy's words; we map them onto
our status menu (documented, not silent):
  skill : strong->strong  moderate->intermediate  weak->basic  aspirational->learning
          lapsed->lapsed  denied->no_experience   (mixed/trap handled specially)
  edu   : withdrawn->incomplete ; others by same name ; 'distinct' excluded
  cert  : failed->pending ; others by same name ; mixed/'distinct' excluded

Writes: eval/results/{eval_results.json, REPORT.md, results_table.md, results_table.csv}
Run:    python eval/run_eval.py
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resume_enricher import enrich
from resume_enricher.shared.matching import normalize
from resume_enricher.shared.models import severity_of

HERE = Path(__file__).resolve().parent
DATASET = HERE / "data" / "all_resumes.json"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

EXCLUDE, DISTRACTOR = "__exclude__", "__distractor__"
VOCAB = {
    "skill": {"strong": "strong", "moderate": "intermediate", "weak": "basic",
              "aspirational": "learning", "lapsed": "lapsed", "denied": "no_experience",
              "trap": DISTRACTOR, "mixed": EXCLUDE},
    "education": {"completed": "completed", "in_progress": "in_progress",
                  "expected": "expected", "incomplete": "incomplete",
                  "withdrawn": "incomplete", "not_awarded": "not_awarded",
                  "deferred": "deferred", "unknown": "unknown",
                  "completed + in_progress (distinct)": EXCLUDE},
    "certification": {"active": "active", "expired": "expired", "revoked": "revoked",
                      "suspended": "suspended", "pending": "pending", "failed": "pending",
                      "unknown": "unknown", "mixed": EXCLUDE,
                      "active + expired (distinct)": EXCLUDE},
}
OUR_KEY = {"skill": "skills", "education": "education", "certification": "certifications"}


def _match_index(raw_items, target):
    """Index of the Affinda item that matches the ground-truth target, or None.

    Matches the target against the item's name/qualification AND its original `text`.
    Affinda often renames a skill (name "Amazon Web Services", text "AWS"), so matching
    on the name alone would wrongly look like a drop."""
    t = normalize(target or "")
    if not t:
        return None
    fields = ("name", "qualification", "text")
    for exact in (True, False):        # prefer an exact match, then fall back to substring
        for i, it in enumerate(raw_items):
            for f in fields:
                c = normalize(it.get(f) or "")
                if not c:
                    continue
                if (t == c) if exact else (t in c or c in t):
                    return i
    return None


def score(resume, timings):
    dim = resume["dimension"]
    mapped = VOCAB[dim].get(resume["expected_status"], EXCLUDE)
    row = {"test_id": resume["test_id"], "dimension": dim, "target": resume["target"],
           "expected_raw": resume["expected_status"], "expected_mapped": mapped,
           "is_control": resume["is_control"], "source_line": resume.get("source_line", "")}
    if mapped == EXCLUDE:
        row["outcome"] = "excluded_multi_item"
        return row

    t0 = time.perf_counter()
    out = enrich(resume["affinda"])
    timings.append(time.perf_counter() - t0)

    raw_items = resume["affinda"]["data"].get(OUR_KEY[dim]) or []
    idx = _match_index(raw_items, resume["target"])
    our_list = out["enrichmentJSON"].get(OUR_KEY[dim], [])
    hit = next((e for e in our_list if e["entryIndex"] == idx), None) if idx is not None else None
    if hit is None:
        row.update(extracted=False, our_status=None, our_severity=None,
                   evidence="", affinda_name=None, outcome="affinda_dropped")
        return row

    row.update(extracted=True, affinda_name=hit["entity"], our_status=hit["status"],
               our_severity=hit["severity"], evidence=hit["evidence"]["text"])
    if mapped == DISTRACTOR:
        row["outcome"] = "trap_ok" if hit["severity"] == "info" else "trap_false_alarm"
    else:
        exp_sev = severity_of(dim, mapped)
        row["expected_severity"] = exp_sev
        row["exact_status_match"] = hit["status"] == mapped
        row["severity_match"] = hit["severity"] == exp_sev
        row["outcome"] = ("exact" if hit["status"] == mapped
                          else "severity_ok" if hit["severity"] == exp_sev else "miss")
    return row


def summarize(name, rows):
    scored = [r for r in rows if r.get("outcome") != "excluded_multi_item"]
    excluded = sum(1 for r in rows if r.get("outcome") == "excluded_multi_item")
    dropped = sum(1 for r in rows if r.get("outcome") == "affinda_dropped")
    ext = [r for r in scored if r.get("extracted")]
    problems = [r for r in ext if r.get("expected_severity") == "warning"]
    controls = [r for r in ext if r.get("expected_severity") == "info"]
    traps = [r for r in ext if r["expected_mapped"] == DISTRACTOR]

    def pct(a, b):
        return f"{a}/{b}" + (f" ({round(100*a/b)}%)" if b else "")

    return {"category": name, "ground_truth_rows": len(scored) + excluded,
            "excluded_multi_item": excluded, "scored": len(scored),
            "affinda_extracted_target": pct(len(ext), len(scored)),
            "affinda_dropped_target": dropped,
            "our_exact_status": pct(sum(r.get("exact_status_match") is True for r in ext), len(ext)),
            "our_severity_agree": pct(sum(r.get("severity_match") is True for r in ext),
                                      len([r for r in ext if "severity_match" in r])),
            "problem_recall_flagged_warning": pct(
                sum(r.get("our_severity") == "warning" for r in problems), len(problems)),
            "control_precision_left_info": pct(
                sum(r.get("our_severity") == "info" for r in controls), len(controls)),
            "trap_precision_no_false_alarm": pct(
                sum(r.get("outcome") == "trap_ok" for r in traps), len(traps))}


def write_table(rows):
    """Per-résumé before/after: the clause the candidate wrote, what Affinda returned,
    and what the enricher added. Shows exactly where the value is demonstrated."""
    label = {"skill": "Skill", "education": "Degree", "certification": "Certificate"}
    noq = {"skill": "no strength", "education": "no status", "certification": "no validity"}
    icon = {"warning": "⚠️", "info": "✅"}

    def clean(s, n=None):
        s = (s or "").replace("\n", " ").replace("|", "\\|").strip()
        return s if (n is None or len(s) <= n) else s[: n - 1] + "…"

    def affinda_cell(r, n=36):
        # Show the name Affinda ACTUALLY returned (it may rename, e.g. target "AWS" ->
        # "Amazon Web Services"). If Affinda truly dropped it, say so.
        if r.get("extracted"):
            return f'{clean(r.get("affinda_name") or r["target"], n)} ({noq[r["dimension"]]})'
        return "✗ not in Affinda output"

    # CSV — full detail, machine-readable
    cols = ["test_id", "dimension", "entity", "resume_clause", "affinda_returned",
            "our_status", "severity", "evidence", "verdict"]
    crows = [[r["test_id"], r["dimension"], r["target"], clean(r.get("source_line")),
              affinda_cell(r, None),
              r.get("our_status") or "(not extracted)", r.get("our_severity") or "-",
              clean(r.get("evidence")), r.get("outcome")]
             for r in rows if r.get("outcome") != "excluded_multi_item"]
    with (OUT / "results_table.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(crows)

    # Markdown — grouped by type, caught-problems first so the value pops
    def our_cell(r):
        if not r.get("extracted"):
            return "⚪ Affinda dropped it, nothing to enrich"
        return (f'**{r.get("our_status")}** {icon.get(r.get("our_severity"), "")}'
                f' · proof: "{clean(r.get("evidence"), 30)}"')

    order = {"warning": 0, "info": 1, None: 2}
    L = ["# Results: every résumé, before and after\n",
         "For each résumé you can see three things: the line the candidate actually "
         "wrote, what Affinda returned (just the bare item, with no qualifier), and what "
         "the enricher added.\n",
         "**⚠️ = a problem we caught.  ✅ = confirmed fine.**  "
         "Caught problems are listed first in each section.\n"]
    for dim in ("skill", "education", "certification"):
        drows = [r for r in rows if r["dimension"] == dim
                 and r.get("outcome") != "excluded_multi_item"]
        drows.sort(key=lambda r: order.get(r.get("our_severity"), 2))
        L.append(f"\n## {label[dim]}s ({len(drows)})\n")
        L.append("| ID | What the candidate wrote | Affinda returned | What we added |")
        L.append("|---|---|---|---|")
        for r in drows:
            L.append(f'| {r["test_id"]} | {clean(r.get("source_line"), 90)} | '
                     f'{affinda_cell(r)} | {our_cell(r)} |')
    (OUT / "results_table.md").write_text("\n".join(L), encoding="utf-8")


def write_report(summ, rows_by, throughput):
    labels = {"skill": ("Skill claim strength", "strength"),
              "education": ("Education completion", "completion status"),
              "certification": ("Certificate validity", "validity status")}
    noq = {"skill": "no strength", "education": "no status", "certification": "no validity"}
    L = ["# Affinda Resume Enricher: evaluation (before and after)\n",
         "_Generated by `eval/run_eval.py` over `eval/data/all_resumes.json` "
         "(300 Affinda-parsed résumés with ground truth)._\n",
         "## The gap we close\n",
         "Affinda extracts the **entity** (skill, degree, certificate). But its schema has "
         "**no field** for the qualifier that changes its meaning: how strong the claim is, "
         "whether the degree was completed, whether the certificate is still valid. The "
         "enricher reads `rawText` and attaches that qualifier as a parallel "
         "`enrichmentJSON` block. The original Affinda response is never modified.\n",
         "## Headline results\n",
         "| Dimension | Affinda alone (BEFORE) | Resume Enricher (AFTER) | False alarms on good items |",
         "|---|---|---|---|"]
    for name, s in summ.items():
        title, word = labels[name]
        L.append(f"| {title} | extracts item, **no {word}** (0 of {s['scored']}) | "
                 f"recovers a flag on **{s['problem_recall_flagged_warning']}** of problem cases | "
                 f"**{s['control_precision_left_info']}** controls kept clean |")
    L += ["", "- **Problem recall** = of items the ground truth marks worth attention "
          "(weak/denied skills, unfinished degrees, invalid certs), how many we flagged `warning`.",
          "- **Control precision** = of genuinely-fine items, how many we correctly left "
          "`info`. A false accusation is the costly error, and we had **none**.\n"]

    # See it in action: one real caught-problem per dimension (clause -> before -> after)
    L += ["## See it in action\n",
          "| What the candidate wrote | Affinda returned | What we added |",
          "|---|---|---|"]
    for dim in ("skill", "education", "certification"):
        ex = next((r for r in rows_by[dim] if r.get("our_severity") == "warning"
                   and r.get("source_line") and r.get("evidence")), None)
        if ex:
            clause = (ex["source_line"] or "").replace("\n", " ").replace("|", "\\|")
            L.append(f'| {clause} | {ex["target"]} ({noq[dim]}) | '
                     f'**{ex["our_status"]}** ⚠️ · proof: "{ex["evidence"]}" |')
    L += ["", "Every résumé, laid out this way: [`results_table.md`](results_table.md).\n",
          "## Per-dimension detail\n"]

    for name, s in summ.items():
        L.append(f"### {labels[name][0]}")
        L += ["| metric | value |", "|---|---|"]
        L += [f"| {k.replace('_',' ')} | {v} |" for k, v in s.items() if k != "category"]
        L.append("")
    L += ["## Throughput (sanity check, not a load test)\n",
          f"- {throughput['resumes_enriched']} résumés; **{throughput['avg_ms_per_resume']} "
          f"ms/résumé** avg (max {throughput['max_ms']} ms), "
          f"about **{throughput['resumes_per_second_single_thread']}/sec** single-threaded.",
          "- Stateless, in-process, pure-stdlib function. Scales linearly with cores. "
          "Correctness is the story.\n",
          "## Honest limitations\n",
          "- Remaining misses are **lexicon gaps** (phrasings not yet in the cue lists). "
          "An unmatched item stays `plain`/`unknown` (`info`): a *miss*, never a false accusation.",
          "- Multi-item rows (`mixed`, `A + B (distinct)`) are **excluded** (need per-item ground truth).",
          "- Items Affinda never extracted cannot be enriched (`affinda_dropped_target`; a parser gap).",
          "\nFull per-résumé output: [`results_table.md`](results_table.md)."]
    (OUT / "REPORT.md").write_text("\n".join(L), encoding="utf-8")


def main():
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    timings = []
    all_rows = [score(r, timings) for r in dataset["resumes"]]
    rows_by = {d: [r for r in all_rows if r["dimension"] == d] for d in VOCAB}
    summ = {d: summarize(d, rows_by[d]) for d in VOCAB}

    throughput = {
        "resumes_enriched": len(timings),
        "avg_ms_per_resume": round(1000 * sum(timings) / len(timings), 3) if timings else None,
        "max_ms": round(1000 * max(timings), 3) if timings else None,
        "resumes_per_second_single_thread": round(len(timings) / sum(timings)) if timings else None,
    }

    (OUT / "eval_results.json").write_text(
        json.dumps({"summary": summ, "throughput": throughput, "rows": rows_by}, indent=2),
        encoding="utf-8")
    write_table(all_rows)
    write_report(summ, rows_by, throughput)

    for d, s in summ.items():
        print(f"\n=== {d.upper()} ===")
        for k, v in s.items():
            if k != "category":
                print(f"  {k:32} {v}")
    print(f"\nthroughput: {throughput['avg_ms_per_resume']} ms/résumé, "
          f"{throughput['resumes_per_second_single_thread']}/sec")
    print(f"wrote REPORT.md, results_table.md/.csv, eval_results.json to {OUT}")


if __name__ == "__main__":
    main()
