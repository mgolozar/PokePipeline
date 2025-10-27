"""Transform API models to DTOs."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pokepipeline.extract.models_api import PokemonAPIModel

from pokepipeline.transform.models_dto import (
    AbilityDTO,
    LoadBatch,
    PokemonAbilityLink,
    PokemonDTO,
    PokemonStatLink,
    PokemonTypeLink,
    StatDTO,
    TypeDTO,
)

logger = logging.getLogger(__name__)

REQUIRED_STATS: set[str] = {
    "hp",
    "attack",
    "defense",
    "special-attack",
    "special-defense",
    "speed",
}


class DropPokemon(Exception):
    pass


def normalize_name(s: str | None) -> str:
    """Normalize string: lowercase and strip.

    >>> normalize_name("Pikachu")
    'pikachu'
    >>> normalize_name("  Charizard  ")
    'charizard'
    >>> normalize_name(None)
    ''
    >>> normalize_name("")
    ''
    """
    if not s:
        return ""
    return s.strip().lower()


def try_extract_id_from_url(url: str | None) -> int | None:
    """Extract ID from URL.

    >>> try_extract_id_from_url("https://pokeapi.co/api/v2/pokemon/25/")
    25
    >>> try_extract_id_from_url("https://pokeapi.co/api/v2/type/12")
    12
    >>> try_extract_id_from_url(None)
    >>> try_extract_id_from_url("invalid")
    """
    if not url:
        return None

    url = url.rstrip("/")
    match = re.search(r"/(\d+)/?$", url)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    return None


def _build_pokemon_dto(api: "PokemonAPIModel") -> PokemonDTO:
    norm_name = normalize_name(api.name)
    if not norm_name:
        raise DropPokemon(f"pokemon {api.id} dropped: empty name")

    return PokemonDTO(
        id=api.id,
        name=norm_name,
        height=api.height or None,
        weight=api.weight or None,
        base_experience=api.base_experience or None,
    )


def _build_type_dtos(api: "PokemonAPIModel") -> tuple[dict[str, TypeDTO], list[PokemonTypeLink]]:
    types_map = {}
    types_links = []

    for t in api.types:
        name = normalize_name(getattr(t, "name", ""))
        if not name:
            logger.warning("skipping empty type name for pokemon %s", api.id)
            continue

        type_id = try_extract_id_from_url(getattr(t, "url", None)) if hasattr(t, "url") else None

        types_map[name] = TypeDTO(id=type_id, name=name)
        types_links.append(PokemonTypeLink(pokemon_id=api.id, type_name=name))

    if not types_links:
        raise DropPokemon(f"pokemon {api.id} dropped: no types")

    return types_map, types_links


def _build_ability_dtos(api: "PokemonAPIModel") -> tuple[dict[str, AbilityDTO], list[PokemonAbilityLink]]:
    abilities_map = {}
    abilities_links = []

    for a in api.abilities:
        name = normalize_name(getattr(a, "name", ""))
        if not name:
            logger.warning("skipping empty ability name for pokemon %s", api.id)
            continue

        ability_id = try_extract_id_from_url(getattr(a, "url", None)) if hasattr(a, "url") else None
        slot = getattr(a, "slot", None)
        is_hidden = bool(getattr(a, "is_hidden", False))

        abilities_map[name] = AbilityDTO(id=ability_id, name=name)
        abilities_links.append(PokemonAbilityLink(
            pokemon_id=api.id,
            ability_name=name,
            is_hidden=is_hidden,
            slot=slot,
        ))

    return abilities_map, abilities_links


def _build_stat_dtos(api: "PokemonAPIModel") -> tuple[dict[str, StatDTO], list[PokemonStatLink]]:
    stats_map = {}
    stats_links = []

    for s in api.stats:
        name = normalize_name(getattr(s, "name", ""))
        if not name:
            logger.warning("skipping empty stat name for pokemon %s", api.id)
            continue

        stat_id = try_extract_id_from_url(getattr(s, "url", None)) if hasattr(s, "url") else None
        base_value = int(getattr(s, "base_stat", 0))
        effort = int(getattr(s, "effort", 0))

        stats_map[name] = StatDTO(id=stat_id, name=name)
        stats_links.append(PokemonStatLink(
            pokemon_id=api.id,
            stat_name=name,
            base_value=base_value,
            effort=effort,
        ))

    return stats_map, stats_links


def api_to_dtos(api: "PokemonAPIModel") -> LoadBatch:
    """Transform PokemonAPIModel to LoadBatch.

    >>> from types import SimpleNamespace
    >>> fake_api = SimpleNamespace(
    ...     id=1, name="Pikachu", height=4, weight=60, base_experience=112,
    ...     types=[SimpleNamespace(name="electric", url="https://api/v2/type/13/")],
    ...     abilities=[SimpleNamespace(name="static")],
    ...     stats=[SimpleNamespace(name="hp", base_stat=35, effort=0)]
    ... )
    >>> batch = api_to_dtos(fake_api)
    >>> batch.pokemons[0].name
    'pikachu'
    >>> len(batch.types)
    1

    Raises:
        DropPokemon: If Pokemon should be excluded from processing
    """
    pokemon_dto = _build_pokemon_dto(api)
    types_map, types_links = _build_type_dtos(api)
    abilities_map, abilities_links = _build_ability_dtos(api)
    stats_map, stats_links = _build_stat_dtos(api)

    collected_stat_names = set(stats_map.keys())
    missing_stats = REQUIRED_STATS - collected_stat_names
    if missing_stats:
        logger.warning(
            "pokemon %s missing standard stats: %s", api.id, sorted(missing_stats)
        )

    return LoadBatch(
        pokemons=[pokemon_dto],
        types=sorted(types_map.values(), key=lambda x: x.name),
        abilities=sorted(abilities_map.values(), key=lambda x: x.name),
        stats=sorted(stats_map.values(), key=lambda x: x.name),
        pokemon_types=types_links,
        pokemon_abilities=abilities_links,
        pokemon_stats=stats_links,
    )
