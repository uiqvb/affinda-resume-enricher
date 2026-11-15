"""The delivery layer — the OUTSIDE DOORS into Resume Enricher.

Nothing here contains any resume logic. Each file is a thin wrapper that takes a
request from the outside world (a terminal command, an HTTP call) and hands it to
the one brain: `resume_enricher.enrich()`. Dependency direction is one-way:

    delivery  ->  app  ->  modules  ->  shared

so these doors may import the engine, but the engine never imports a door.
"""
