"""The HTTP door (built with FastAPI).

Turns Resume Enricher into a tiny web service. A data platform (e.g. a SEEK-type
pipeline) POSTs an Affinda response and gets back the EnrichedJSON.

Run it locally:

    uvicorn resume_enricher.delivery.api:app --reload
    # then open http://127.0.0.1:8000/docs  for an auto-generated test page

Endpoints:
    GET  /health   -> {"status": "ok"}        (is the service alive?)
    POST /enrich   -> EnrichedJSON             (the actual work)

Like the CLI, this file holds NO resume logic. It validates nothing itself — it
just hands the incoming JSON to `enrich()` and turns any complaint into a tidy
HTTP error.
"""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException

from resume_enricher import enrich

app = FastAPI(
    title="Resume Enricher",
    version="1.0",
    description=(
        "Enriches an Affinda Resume-Parser response. The original is returned "
        "untouched under `originalJSON`; our added status / severity / evidence "
        "records sit alongside under `enrichmentJSON`."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    """A cheap liveness check — handy for Docker / load balancers."""
    return {"status": "ok"}


@app.post("/enrich")
def enrich_endpoint(
    affinda: dict[str, Any] = Body(
        ...,
        description="A full Affinda Resume-Parser response (must contain a `data` object).",
    )
) -> dict[str, Any]:
    """Enrich one Affinda response and return `{ originalJSON, enrichmentJSON }`."""
    try:
        return enrich(affinda)
    except ValueError as err:
        # Bad input shape -> 422 Unprocessable Entity, with the plain-English reason.
        raise HTTPException(status_code=422, detail=str(err))
