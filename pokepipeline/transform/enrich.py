"""Enrichment stage for computing derived Pokemon fields."""

from __future__ import annotations

from pokepipeline.transform.models_dto import LoadBatch, PokemonDTO, PokemonStatLink

REQUIRED_STATS = {"hp", "attack", "defense", "special-attack", "special-defense", "speed"}


def _compute_unit_conversions(p: PokemonDTO) -> tuple[float | None, float | None]:
    """Convert height to meters and weight to kilograms."""
    m = p.height / 10.0 if p.height is not None else None
    kg = p.weight / 10.0 if p.weight is not None else None
    return m, kg


def _compute_bst_for_pokemon(pokemon_id: int, links: list[PokemonStatLink]) -> int | None:
    """Compute base stat total for a pokemon."""
    stats = {
        link.stat_name: link.base_value
        for link in links
        if link.pokemon_id == pokemon_id and link.stat_name in REQUIRED_STATS
    }
    if not stats:
        return None
    return sum(stats.get(stat, 0) for stat in REQUIRED_STATS)


def _compute_bulk_index(m: float | None, kg: float | None) -> float | None:
    """Compute bulk index: kg / (m ** 2)."""
    if not m or not kg or m <= 0:
        return None
    return kg / (m * m)


def enrich_and_derive(lb: LoadBatch) -> LoadBatch:
    """Enrich PokemonDTOs with derived fields.

    Computes height_m, weight_kg, base_stat_total, and bulk_index.
    Returns new LoadBatch with enriched pokemons.
    """
    stat_links = list(lb.pokemon_stats)

    enriched_pokemons = []
    for p in lb.pokemons:
        m, kg = _compute_unit_conversions(p)
        bst = _compute_bst_for_pokemon(p.id, stat_links)
        bulk = _compute_bulk_index(m, kg)

        enriched = p.model_copy(
            update={
                "height_m": m,
                "weight_kg": kg,
                "base_stat_total": bst,
                "bulk_index": bulk,
            }
        )
        enriched_pokemons.append(enriched)

    return lb.model_copy(update={"pokemons": enriched_pokemons})
