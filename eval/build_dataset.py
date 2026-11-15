"""Build the ONE centralized test-resume file: eval/data/all_resumes.json.

This bundles the whole DAY-2 corpus (100 skill + 100 education + 100
certification Affinda responses, each with its ground-truth label) into a single,
self-contained JSON so this repo can run its evaluation WITHOUT the separate
process/proof repo.

Provenance: the résumés are synthetic (authored in the process repo's taxonomy),
rendered to PDF, and parsed through the Affinda Sandbox (schema v1). We keep only
the fields the enricher actually reads — `rawText` plus the three extracted lists —
so the file stays lean and auditable.

Run (needs the process repo's DAY-2 folder alongside):
    python eval/build_dataset.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent.parent / "DAY-2 - Planning" / "experiments"
OUT = HERE / "data" / "all_resumes.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

CATS = {
    "skill": ("skill/results/skill-responses-100.json",
              "skill/ground_truth_skill.json", "expected_strength", "skill"),
    "education": ("education/results/education-responses-100.json",
                  "education/ground_truth_education.json",
                  "expected_completion_status", "qualification"),
    "certification": ("certification/results/certification-responses-100.json",
                      "certification/ground_truth_certification.json",
                      "expected_validity_status", "cert_name"),
}
KEEP = ("rawText", "skills", "education", "certifications")


def main():
    resumes = []
    for dim, (resp_f, gt_f, status_key, name_key) in CATS.items():
        responses = json.loads((SRC / resp_f).read_text(encoding="utf-8"))
        gt = json.loads((SRC / gt_f).read_text(encoding="utf-8"))
        by_id = {Path(r.get("fileName", "")).stem: r for r in responses}
        for test_id, meta in gt.items():
            if not isinstance(meta, dict) or status_key not in meta:
                continue
            rec = by_id.get(test_id)
            if rec is None:
                continue
            data = rec["response"]["data"]
            resumes.append({
                "test_id": test_id,
                "dimension": dim,
                "target": meta.get(name_key, ""),
                "expected_status": meta[status_key],
                "is_control": str(meta.get("is_control", "")).lower() == "true",
                "is_distractor": str(meta.get("is_distractor", "")).lower() == "true",
                "source_line": meta.get("exact_source_line", meta.get("phrasing", "")),
                # exactly what we feed enrich(): an Affinda response with top-level data
                "affinda": {"data": {k: data.get(k) for k in KEEP if k in data}},
            })

    out = {
        "meta": {
            "description": "Centralized test corpus for the Affinda Resume Enricher.",
            "provenance": "Synthetic résumés (process repo taxonomy) -> PDF -> Affinda "
                          "Sandbox v1 parse. Only enricher-relevant fields kept.",
            "count": len(resumes),
            "by_dimension": {d: sum(r["dimension"] == d for r in resumes) for d in CATS},
        },
        "resumes": resumes,
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT}  ({len(resumes)} resumes, {kb:.0f} KB)")


if __name__ == "__main__":
    main()
