"""The registry — the ONE place features are listed.

Adding a new feature later = one more line here (plus its module folder).
Each line maps:  name -> (its run function,  Affinda input key,  our output key)
"""
from __future__ import annotations

from resume_enricher.modules import certification, education, skill

REGISTRY = {
    "skill":         (skill.run,         "skills",         "skills"),
    "education":     (education.run,      "education",      "education"),
    "certification": (certification.run, "certifications", "certifications"),
}
