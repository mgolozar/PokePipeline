"""Essential tests for transform mapping module (minimal, high-signal)."""

import pytest
from types import SimpleNamespace

from pokepipeline.transform.mapping import DropPokemon, api_to_dtos


def _make_fake_api(
    id=1,
    name="Pikachu",
    height=4,
    weight=60,
    base_experience=112,
    types=None,
    abilities=None,
    stats=None,
):
    if types is None:
        types = [SimpleNamespace(name="electric")]
    if abilities is None:
        abilities = [SimpleNamespace(name="static")]
    if stats is None:
        stats = [
            SimpleNamespace(name="hp", base_stat=35, effort=0),
            SimpleNamespace(name="attack", base_stat=55, effort=0),
        ]

    return SimpleNamespace(
        id=id,
        name=name,
        height=height,
        weight=weight,
        base_experience=base_experience,
        types=types,
        abilities=abilities,
        stats=stats,
    )


class TestApiToDtos:
    def test_valid_pokemon_minimal_happy_path(self):
        fake_api = _make_fake_api(
            types=[SimpleNamespace(name="electric", url="https://pokeapi.co/api/v2/type/13/")]
        )
        batch = api_to_dtos(fake_api)

        assert len(batch.pokemons) == 1
        p = batch.pokemons[0]
        assert (p.id, p.name, p.height, p.weight) == (1, "pikachu", 4, 60)
        assert len(batch.types) >= 1
        assert len(batch.pokemon_types) >= 1
        assert len(batch.stats) >= 1
        assert len(batch.pokemon_stats) >= 1

    def test_no_types_raises_drop_pokemon(self):
        fake_api = _make_fake_api(types=[])
        with pytest.raises(DropPokemon, match="no types"):
            api_to_dtos(fake_api)

    def test_sorted_output_for_determinism(self):
        fake_api = _make_fake_api(
            types=[SimpleNamespace(name="electric"), SimpleNamespace(name="normal")],
            abilities=[SimpleNamespace(name="static"), SimpleNamespace(name="lightning-rod")],
            stats=[
                SimpleNamespace(name="hp", base_stat=35, effort=0),
                SimpleNamespace(name="attack", base_stat=55, effort=0),
            ],
        )
        batch = api_to_dtos(fake_api)

        assert [t.name for t in batch.types] == sorted([t.name for t in batch.types])
        assert [a.name for a in batch.abilities] == sorted([a.name for a in batch.abilities])
        assert [s.name for s in batch.stats] == sorted([s.name for s in batch.stats])
