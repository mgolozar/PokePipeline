"""Tests for transform enrichment module."""

import pytest

from pokepipeline.transform.enrich import (
    _compute_bst_for_pokemon,
    _compute_bulk_index,
    _compute_unit_conversions,
    enrich_and_derive,
)
from pokepipeline.transform.models_dto import (
    LoadBatch,
    PokemonDTO,
    PokemonStatLink,
    TypeDTO,
    AbilityDTO,
    StatDTO,
    PokemonTypeLink,
    PokemonAbilityLink,
)


class TestUnitConversions:
    """Test unit conversion calculations."""

    def test_converts_units_correctly(self):
        """Test height and weight conversions."""
        p = PokemonDTO(id=1, name="test", height=4, weight=60)
        m, kg = _compute_unit_conversions(p)
        assert m == 0.4
        assert kg == 6.0

    def test_handles_none_values(self):
        """Test None values return None."""
        p = PokemonDTO(id=1, name="test", height=None, weight=None)
        m, kg = _compute_unit_conversions(p)
        assert m is None
        assert kg is None

    def test_zero_values(self):
        """Test zero values are converted correctly."""
        p = PokemonDTO(id=1, name="test", height=0, weight=0)
        m, kg = _compute_unit_conversions(p)
        assert m == 0.0
        assert kg == 0.0


class TestBSTComputation:
    """Test base stat total computation."""

    def test_computes_bst_for_all_required_stats(self):
        """Test BST is sum of all 6 required stats."""
        links = [
            PokemonStatLink(pokemon_id=1, stat_name="hp", base_value=35, effort=0),
            PokemonStatLink(pokemon_id=1, stat_name="attack", base_value=49, effort=0),
            PokemonStatLink(pokemon_id=1, stat_name="defense", base_value=49, effort=0),
            PokemonStatLink(pokemon_id=1, stat_name="special-attack", base_value=65, effort=0),
            PokemonStatLink(pokemon_id=1, stat_name="special-defense", base_value=65, effort=0),
            PokemonStatLink(pokemon_id=1, stat_name="speed", base_value=45, effort=0),
        ]
        bst = _compute_bst_for_pokemon(1, links)
        assert bst == 308

    def test_returns_none_when_no_stats(self):
        """Test returns None when no stats present."""
        links = []
        bst = _compute_bst_for_pokemon(1, links)
        assert bst is None

    def test_filters_required_stats_only(self):
        """Test only counts required stats, ignores others."""
        links = [
            PokemonStatLink(pokemon_id=1, stat_name="hp", base_value=10, effort=0),
            PokemonStatLink(pokemon_id=1, stat_name="random-stat", base_value=999, effort=0),
        ]
        bst = _compute_bst_for_pokemon(1, links)
        assert bst == 10


class TestBulkIndex:
    """Test bulk index computation."""

    def test_computes_bulk_index_correctly(self):
        """Test bulk index calculation."""
        bulk = _compute_bulk_index(0.4, 6.0)
        assert abs(bulk - 37.5) < 0.0001

    def test_returns_none_when_height_missing(self):
        """Test returns None when height is missing."""
        assert _compute_bulk_index(None, 6.0) is None

    def test_returns_none_when_weight_missing(self):
        """Test returns None when weight is missing."""
        assert _compute_bulk_index(0.4, None) is None

    def test_returns_none_when_height_zero(self):
        """Test returns None when height is zero."""
        assert _compute_bulk_index(0.0, 6.0) is None


class TestEnrichAndDerive:
    """Test the main enrich_and_derive function."""

    def test_enrich_is_pure_and_keeps_other_lists_intact(self):
        """Test enrichment is pure and doesn't modify other lists."""
        pokemon = PokemonDTO(id=1, name="test", height=4, weight=60)
        types = [TypeDTO(id=1, name="grass")]
        abilities = [AbilityDTO(id=1, name="overgrow")]
        stats = [StatDTO(id=1, name="hp")]
        pokemon_types = [PokemonTypeLink(pokemon_id=1, type_name="grass")]
        pokemon_abilities = [
            PokemonAbilityLink(pokemon_id=1, ability_name="overgrow", is_hidden=False, slot=1)
        ]
        pokemon_stats = [PokemonStatLink(pokemon_id=1, stat_name="hp", base_value=35, effort=0)]

        lb = LoadBatch(
            pokemons=[pokemon],
            types=types,
            abilities=abilities,
            stats=stats,
            pokemon_types=pokemon_types,
            pokemon_abilities=pokemon_abilities,
            pokemon_stats=pokemon_stats,
        )

        enriched = enrich_and_derive(lb)

        # Original lists unchanged
        assert enriched.types == types
        assert enriched.abilities == abilities
        assert enriched.stats == stats
        assert enriched.pokemon_types == pokemon_types
        assert enriched.pokemon_abilities == pokemon_abilities
        assert enriched.pokemon_stats == pokemon_stats

        # Pokemon enriched
        assert enriched.pokemons[0].height_m == 0.4
        assert enriched.pokemons[0].weight_kg == 6.0

    def test_enriches_multiple_pokemon(self):
        """Test enrichment works with multiple pokemon."""
        pokemon1 = PokemonDTO(id=1, name="test1", height=4, weight=60)
        pokemon2 = PokemonDTO(id=2, name="test2", height=6, weight=85)

        lb = LoadBatch(
            pokemons=[pokemon1, pokemon2],
            types=[],
            abilities=[],
            stats=[],
            pokemon_types=[],
            pokemon_abilities=[],
            pokemon_stats=[],
        )

        enriched = enrich_and_derive(lb)

        assert len(enriched.pokemons) == 2
        assert enriched.pokemons[0].height_m == 0.4
        assert enriched.pokemons[1].height_m == 0.6

    def test_handles_missing_data_gracefully(self):
        """Test handles missing data by setting fields to None."""
        pokemon = PokemonDTO(id=1, name="test", height=None, weight=None)

        lb = LoadBatch(
            pokemons=[pokemon],
            types=[],
            abilities=[],
            stats=[],
            pokemon_types=[],
            pokemon_abilities=[],
            pokemon_stats=[],
        )

        enriched = enrich_and_derive(lb)

        assert enriched.pokemons[0].height_m is None
        assert enriched.pokemons[0].weight_kg is None
        assert enriched.pokemons[0].base_stat_total is None
        assert enriched.pokemons[0].bulk_index is None
