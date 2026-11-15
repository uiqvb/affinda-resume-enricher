"""Resume Enricher.

Affinda reads a resume and pulls out skills, degrees and certificates — but it
drops the small print. It will list "SQL" even when the resume says "no
experience with SQL", or list a certificate that has actually expired.

Resume Enricher reads that same resume text and adds the small print back, as notes
kept separate from Affinda's own data. It never changes the original.

The main entry point, enrich(), gets wired together later (build step 6). For
now the groundwork lives in resume_enricher.shared.
"""

__version__ = "1.0.0"

# The one thing people use: enrich(affinda) -> { originalJSON, enrichmentJSON }
from resume_enricher.app.enrich import enrich  # noqa: E402

__all__ = ["enrich", "__version__"]
