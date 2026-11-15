"""The orchestrator — the whole pipeline in one method.

Steps:
  1. validate the input (bouncer)
  2. deep-copy it (photocopier) and read the items from the copy
  3. run each registered feature -> one Enrichment per item
  4. roll the WARNINGS up into a plain-English summary
  5. prove the original is untouched (auditor)
  6. hand back { originalJSON, enrichmentJSON }
"""
from __future__ import annotations

from resume_enricher.app.registry import REGISTRY
from resume_enricher.shared.validators import deep_copy, ensure_untouched, validate_input

_LABELS = {"skills": "Skill", "education": "Degree", "certifications": "Certificate"}

"""Enrich one Affinda response. Returns { originalJSON, enrichmentJSON }."""
def enrich(affinda:dict , modules=None):

    #names becomes a list of keys from REGISTERY DICT
    names = list(modules) if modules else list(REGISTRY.keys())

    validate_input(affinda)                       # 1. check if input is valid
    original = deep_copy(affinda)                 # 2. creates a deep copy(which means they point to different dictionaries)

    
    data = original.get("data",) 
    raw_text = data.get("rawText","")

    enrichment = {
        "version": "1.0",
        "checksRun": names,
        "skills": [],
        "education": [],
        "certifications": [],
        "summary": [],
    }

    for name in names:                            # 3. iterate through names list for every key and store the values of that key into these variables
        run_fn, input_key, output_key = REGISTRY[name] #store them in these vars !!!see shape of registery key and values to understand
        enrichment[output_key] = run_fn(data.get(input_key) or [], raw_text) #use the vars to run each function on the data of orignial json and its rawtext, and store it in enrichment dict

    enrichment["summary"] = _build_summary(enrichment)   # 4. roll up the warnings into a summary

    ensure_untouched(affinda, original)           # 5. prove we changed nothing through ensure untouched function

    return {"originalJSON": original, "enrichmentJSON": enrichment}   # 6.Return the enrichedJSON= originalJSON +enrichmentJSON


def _build_summary(enrichment):

    """One plain-English line per WARNING (the stuff a recruiter should see)."""
    lines = []
    for key, label in _LABELS.items():
        for e in enrichment[key]:
            if e["severity"] == "warning":
                pretty = e["status"].replace("_", " ")
                lines.append(f"{label} '{e['entity']}' looks {pretty}.")
    return lines
