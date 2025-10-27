"""Tests for quality checks module."""

import pytest
from types import SimpleNamespace

from pokepipeline.quality.checks import ensure_has_type, ensure_required_stats, validate_loadbatch
from pokepipeline.transform.mapping import api_to_dtos


def _make_fake_api_with_all_stats():
    return SimpleNamespace(
        id=1,
        name="Pikachu",
        height=4,
        weight=60,
        base_experience=112,
        types=[SimpleNamespace(name="electric")],
        abilities=[SimpleNamespace(name="static")],
        stats=[
            SimpleNamespace(name="hp", base_stat=35, effort=0),
            SimpleNamespace(name="attack", base_stat=55, effort=0),
            SimpleNamespace(name="defense", base_stat=40, effort=0),
            SimpleNamespace(name="special-attack", base_stat=50, effort=0),
            SimpleNamespace(name="special-defense", base_stat=50, effort=0),
            SimpleNamespace(name="speed", base_stat=90, effort=0),
        ],
    )


class TestEnsureRequiredStats:
    def test_all_required_stats_present(self):
        fake_api = _make_fake_api_with_all_stats()
        batch = api_to_dtos(fake_api)
        is_valid, reason = ensure_required_stats(batch)
        assert is_valid
        assert reason is None

    def test_missing_required_stats(self):
        fake_api = SimpleNamespace(
            id=1,
            name="Pikachu",
            height=4,
            weight=60,
            base_experience=112,
            types=[SimpleNamespace(name="electric")],
            abilities=[SimpleNamespace(name="static")],
            stats=[
                SimpleNamespace(name="hp", base_stat=35, effort=0),
                SimpleNamespace(name="attack", base_stat=55, effort=0),
            ],
        )
        batch = api_to_dtos(fake_api)
        is_valid, reason = ensure_required_stats(batch)
        assert not is_valid
        assert "defense" in reason
        assert "special-attack" in reason


class TestEnsureHasType:
    def test_has_types(self):
        fake_api = SimpleNamespace(
            id=1,
            name="Pikachu",
            height=4,
            weight=60,
            base_experience=112,
            types=[SimpleNamespace(name="electric")],
            abilities=[SimpleNamespace(name="static")],
            stats=[SimpleNamespace(name="hp", base_stat=35, effort=0)],
        )
        batch = api_to_dtos(fake_api)
        is_valid, reason = ensure_has_type(batch)
        assert is_valid
        assert reason is None

    def test_no_types(self):
        fake_api = SimpleNamespace(
            id=1,
            name="Pikachu",
            height=4,
            weight=60,
            base_experience=112,
            types=[],
            abilities=[SimpleNamespace(name="static")],
            stats=[SimpleNamespace(name="hp", base_stat=35, effort=0)],
        )
        with pytest.raises(Exception):
            batch = api_to_dtos(fake_api)


class TestValidateLoadbatch:
    def test_valid_loadbatch(self):
        fake_api = _make_fake_api_with_all_stats()
        batch = api_to_dtos(fake_api)
        is_valid, reasons = validate_loadbatch(batch)
        assert is_valid
        assert reasons == []

    def test_invalid_loadbatch_missing_stats(self):
        fake_api = SimpleNamespace(
            id=1,
            name="Pikachu",
            height=4,
            weight=60,
            base_experience=112,
            types=[SimpleNamespace(name="electric")],
            abilities=[SimpleNamespace(name="static")],
            stats=[
                SimpleNamespace(name="hp", base_stat=35, effort=0),
                SimpleNamespace(name="attack", base_stat=55, effort=0),
            ],
        )
        batch = api_to_dtos(fake_api)
        is_valid, reasons = validate_loadbatch(batch)
        assert not is_valid
        assert len(reasons) > 0
        assert any("missing required stats" in r for r in reasons)
