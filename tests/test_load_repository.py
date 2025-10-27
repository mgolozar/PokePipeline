"""Tests for load repository."""

import pytest
from types import SimpleNamespace

from pokepipeline.load.repository import Repository
from pokepipeline.transform.mapping import api_to_dtos
from pokepipeline.transform.models_dto import LoadBatch


def _make_fake_api_with_all_stats():
    return SimpleNamespace(
        id=1,
        name="Pikachu",
        height=4,
        weight=60,
        base_experience=112,
        types=[
            SimpleNamespace(name="electric", url="https://pokeapi.co/api/v2/type/13/")
        ],
        abilities=[
            SimpleNamespace(name="static", url="https://pokeapi.co/api/v2/ability/9/")
        ],
        stats=[
            SimpleNamespace(name="hp", base_stat=35, effort=0, url="https://pokeapi.co/api/v2/stat/1/"),
            SimpleNamespace(name="attack", base_stat=55, effort=0, url="https://pokeapi.co/api/v2/stat/2/"),
            SimpleNamespace(name="defense", base_stat=40, effort=0, url="https://pokeapi.co/api/v2/stat/3/"),
            SimpleNamespace(name="special-attack", base_stat=50, effort=0, url="https://pokeapi.co/api/v2/stat/4/"),
            SimpleNamespace(name="special-defense", base_stat=50, effort=0, url="https://pokeapi.co/api/v2/stat/5/"),
            SimpleNamespace(name="speed", base_stat=90, effort=0, url="https://pokeapi.co/api/v2/stat/6/"),
        ],
    )


class TestRepository:
    @pytest.mark.skip(reason="Database fixture not available")
    def test_load_batch_basic(self, db_engine):
        """Test loading a basic batch."""
        fake_api = _make_fake_api_with_all_stats()
        batch = api_to_dtos(fake_api)
        
        repo = Repository(db_engine)
        metrics = repo.load_batch(batch)
        
        assert metrics["upserted_pokemon"] == 1
        assert metrics["inserted_types"] >= 0
        assert metrics["inserted_abilities"] >= 0
        assert metrics["inserted_stats"] >= 0
        assert metrics["inserted_links"]["types"] >= 0
        assert metrics["inserted_links"]["abilities"] >= 0
        assert metrics["inserted_links"]["stats"] >= 0

    @pytest.mark.skip(reason="Database fixture not available")
    def test_load_batch_idempotent(self, db_engine):
        """Test that loading the same batch twice doesn't create duplicates."""
        fake_api = _make_fake_api_with_all_stats()
        batch = api_to_dtos(fake_api)
        
        repo = Repository(db_engine)
        
        # First load
        metrics1 = repo.load_batch(batch)
        assert metrics1["upserted_pokemon"] == 1
        
        # Second load - should be idempotent
        metrics2 = repo.load_batch(batch)
        assert metrics2["upserted_pokemon"] == 1
        # Links should be 0 on second run since they already exist
        assert metrics2["inserted_links"]["types"] == 0
        assert metrics2["inserted_links"]["abilities"] == 0
        assert metrics2["inserted_links"]["stats"] == 0

    @pytest.mark.skip(reason="Database fixture not available")
    def test_load_batch_empty(self, db_engine):
        """Test loading an empty batch."""
        empty_batch = LoadBatch(
            pokemons=[],
            types=[],
            abilities=[],
            stats=[],
            pokemon_types=[],
            pokemon_abilities=[],
            pokemon_stats=[],
        )
        
        repo = Repository(db_engine)
        metrics = repo.load_batch(empty_batch)
        
        assert metrics["upserted_pokemon"] == 0
