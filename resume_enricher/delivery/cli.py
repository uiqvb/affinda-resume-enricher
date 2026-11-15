"""The COMMAND-LINE door (built with typer).

Lets a person run Resume Enricher from a terminal on a JSON file:

    python -m resume_enricher.delivery.cli sample.json
    python -m resume_enricher.delivery.cli sample.json --summary
    python -m resume_enricher.delivery.cli sample.json --enrichment-only

(There's a single command, so no sub-command name is needed — the file comes
first, then any options.)

This file holds NO resume logic. It only: reads a JSON file, calls the one brain
`enrich()`, and prints the result. Everything clever happens inside `enrich()`.
"""
from __future__ import annotations

import json
from pathlib import Path

import typer

from resume_enricher import enrich

app = typer.Typer(
    add_completion=False,
    help="Resume Enricher — enrich Affinda resume JSON with status, severity and evidence.",
)


@app.command(name="enrich")
def enrich_cmd(
    file: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        metavar="FILE",
        help="Path to an Affinda response JSON file.",
    ),
    enrichment_only: bool = typer.Option(
        False, "--enrichment-only", help="Print only the enrichmentJSON (what we added)."
    ),
    summary: bool = typer.Option(
        False, "--summary", help="Print only the plain-English warning summary."
    ),
    indent: int = typer.Option(2, "--indent", help="Spaces to indent the JSON output."),
) -> None:
    """Enrich one Affinda resume JSON file and print the result."""
    # 1. read the file the person pointed at
    try:
        affinda = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        typer.secho(f"That file isn't valid JSON: {err}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    # 2. hand it to the one brain (this is the only line that does real work)
    try:
        result = enrich(affinda)
    except ValueError as err:
        typer.secho(f"Can't enrich this resume: {err}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # 3. print whichever view was asked for
    if summary:
        lines = result["enrichmentJSON"]["summary"]
        if not lines:
            typer.echo("No warnings — nothing stood out.")
        for line in lines:
            typer.echo(f"- {line}")
        return

    payload = result["enrichmentJSON"] if enrichment_only else result
    typer.echo(json.dumps(payload, indent=indent))


def main() -> None:
    """Entry point so `python -m resume_enricher.delivery.cli ...` works."""
    app()


if __name__ == "__main__":
    main()
