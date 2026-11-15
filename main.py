"""The smallest way to RUN Resume Enricher and see the whole picture.

Run it from inside the `resume_enricher/` folder:

    python main.py                 # enrich a built-in sample resume
    python main.py some_resume.json  # enrich a resume JSON file you point at

It prints the full EnrichedJSON: Affinda's original (untouched) + our enrichmentJSON.
"""
from __future__ import annotations

import json
import sys

from resume_enricher import enrich

# A tiny hand-made Affinda-style response, with problems baked in so you can see
# the enricher react: a denied skill, a learned skill, a withdrawn degree, an
# expired certificate — plus one perfectly fine skill (Python) for contrast.
SAMPLE = {
    "data": {
        "skills": [
            {"name": "SQL"},
            {"name": "Python"},
            {"name": "Excel"},
        ],
        "education": [
                                            {"qualification": "BSc Computer Science"},
        ],
        "certifications": [
            {"name": "AWS Certified Solutions Architect"},
        ],

        "rawText":
        (
            "Skills: no experience with SQL, expert in Python, learning Excel. "
            "Education: BSc Computer Science (withdrew 2016). "
            "Certifications: AWS Certified Solutions Architect (expired 2021)."
        ),



    }
}


def main() -> None:

    if len(sys.argv) > 1:

        with open(sys.argv[1], encoding="utf-8") as f:
            affinda = json.load(f)
            
    else:
        affinda = SAMPLE

    result = enrich(affinda)

    # Print the enrichment part first (the interesting bit), then the full object.
    print("=== enrichmentJSON (what we added) ===")
    print(json.dumps(result["enrichmentJSON"], indent=2))
    print("\n=== summary (the warnings, in plain English) ===")
    for line in result["enrichmentJSON"]["summary"]:
        print("  -", line)


if __name__ == "__main__":
    main()
