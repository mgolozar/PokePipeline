"""Main orchestrator for the Pokemon data pipeline."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from pokepipeline.config import settings
from pokepipeline.extract.client import PokemonClient
from pokepipeline.load.db import get_engine
from pokepipeline.load.repository import Repository
from pokepipeline.quality.checks import validate_loadbatch
from pokepipeline.transform.mapping import DropPokemon, api_to_dtos
from pokepipeline.transform.enrich import enrich_and_derive

logger = logging.getLogger(__name__)


async def run_job(limit: int, offset: int = 0, ids: list[int] | None = None) -> dict[str, Any]:
    """Execute the full ETL pipeline for given Pokemon."""
    start_time = time.time()
    metrics = {
        "fetched": 0,
        "transformed": 0,
        "loaded": 0,
        "dropped": 0,
        "errors": 0,
        "duration_sec": 0.0,
    }

    client = PokemonClient(
        timeout=settings.REQUEST_TIMEOUT_SEC,
        rate_limit_per_sec=settings.RATE_LIMIT_PER_SEC,
        concurrency=settings.HTTP_CONCURRENCY,
    )

    if ids is None:
        logger.info(f"Fetching pokemon IDs: limit={limit}, offset={offset}")
        ids = await client.fetch_pokemon_ids(limit=limit, offset=offset)
        logger.info(f"Found {len(ids)} pokemon to process")

    if not ids:
        logger.warning("No pokemon IDs to process")
        return metrics

    logger.info(f"Extracting data for {len(ids)} pokemon")
    pokemon_data = await _extract_all(client, ids)
    metrics["fetched"] = len(pokemon_data)
    logger.info(f"Extracted {len(pokemon_data)} pokemon")

    repository = Repository(get_engine())
    
    for api_data in pokemon_data:
        try:
            _process_pokemon(api_data, repository, metrics, settings)
        except DropPokemon as e:
            logger.warning(f"Pokemon {api_data.id} dropped: {e}")
            metrics["dropped"] += 1
        except Exception as e:
            logger.error(f"Error processing pokemon {api_data.id}: {e}", exc_info=True)
            metrics["errors"] += 1

    metrics["duration_sec"] = time.time() - start_time
    logger.info(
        f"Pipeline complete: fetched={metrics['fetched']}, "
        f"transformed={metrics['transformed']}, loaded={metrics['loaded']}, "
        f"dropped={metrics['dropped']}, errors={metrics['errors']}, "
        f"duration={metrics['duration_sec']:.2f}s"
    )

    return metrics


def _process_pokemon(api_data: Any, repository: Repository, metrics: dict, settings: Any) -> None:
    """Process a single pokemon through transform and load."""
    batch = api_to_dtos(api_data)
    
    if settings.TRANSFORM_ENABLE_ENRICH:
        batch = enrich_and_derive(batch)
    
    metrics["transformed"] += 1
    
    is_valid, reasons = validate_loadbatch(batch)
    if not is_valid:
        logger.warning(f"Pokemon {api_data.id} failed quality checks: {reasons}")
        metrics["dropped"] += 1
        return
    
    repository.load_batch(batch)
    metrics["loaded"] += 1


async def _extract_all(client: PokemonClient, ids: list[int]) -> list[Any]:
    """Extract pokemon data concurrently."""
    tasks = [client.fetch_pokemon(pokemon_id) for pokemon_id in ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    pokemon_data = [r for r in results if not isinstance(r, Exception)]
    for error in results:
        if isinstance(error, Exception):
            logger.error(f"Extraction error: {error}")
    
    return pokemon_data


def run_job_sync(limit: int, offset: int = 0, ids: list[int] | None = None) -> dict[str, Any]:
    """Synchronous wrapper for run_job."""
    return asyncio.run(run_job(limit=limit, offset=offset, ids=ids))




