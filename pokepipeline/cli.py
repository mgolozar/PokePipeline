"""CLI interface for PokePipeline."""

from __future__ import annotations

import typer

from pokepipeline.config import settings
from pokepipeline.logging_setup import configure_logging
from pokepipeline.orchestrator import run_job_sync

app = typer.Typer(help="Run the Pokemon data pipeline.")


@app.command()
def run(
    limit: int = typer.Option(settings.TARGET_LIMIT, "--limit", "-l", help="Number of pokemon to fetch"),
    offset: int = typer.Option(settings.TARGET_OFFSET, "--offset", "-o", help="Offset for pokemon fetching"),
) -> None:
    """Run the Pokemon data pipeline."""
    configure_logging(settings.LOG_LEVEL)
    
    typer.echo("Running PokePipeline...")
    metrics = run_job_sync(limit=limit, offset=offset)
    _display_summary(metrics)


def _display_summary(metrics: dict) -> None:
    """Display pipeline execution summary."""
    typer.echo("\nPipeline Summary:")
    typer.echo(f"  Fetched: {metrics['fetched']}")
    typer.echo(f"  Transformed: {metrics['transformed']}")
    typer.echo(f"  Loaded: {metrics['loaded']}")
    typer.echo(f"  Dropped: {metrics['dropped']}")
    typer.echo(f"  Errors: {metrics['errors']}")
    typer.echo(f"  Duration: {metrics['duration_sec']:.2f}s")
    
    if metrics["errors"] == 0:
        typer.echo("\nPipeline completed successfully!")
    else:
        typer.echo(f"\nPipeline completed with {metrics['errors']} errors")


if __name__ == "__main__":
    app()

