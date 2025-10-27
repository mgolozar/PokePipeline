"""Core extract tests (minimal)."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from pokepipeline.extract.client import PokemonClient


class _MockResponse:
    """Minimal mock response for httpx."""

    def __init__(self, data: dict, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def json(self) -> dict:
        return self._data

    def raise_for_status(self) -> None:
        if 400 <= self.status_code:
            raise httpx.HTTPStatusError(
                message="error",
                request=httpx.Request("GET", "https://pokeapi.co/"),
                response=httpx.Response(self.status_code),
            )


class TestFetchPokemonIds:
    @pytest.mark.asyncio
    async def test_fetch_pokemon_ids_success(self):
        """Parses integer IDs from URL strings (unit, mocked)."""
        payload = {
            "count": 100,
            "results": [
                {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
                {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
            ],
        }
        client = PokemonClient(rate_limit_per_sec=1000, concurrency=10)
        with patch.object(httpx.AsyncClient, "get", return_value=_MockResponse(payload)):
            ids = await client.fetch_pokemon_ids(limit=2, offset=0)
        assert ids == [1, 2]


class TestFetchPokemon:
    @pytest.mark.asyncio
    async def test_fetch_pokemon_success(self):
        """Maps API response to simplified model (unit, mocked)."""
        payload = {
            "id": 1,
            "name": "bulbasaur",
            "height": 7,
            "weight": 69,
            "base_experience": 64,
            "types": [
                {"slot": 1, "type": {"name": "grass", "url": "https://pokeapi.co/api/v2/type/12/"}},
                {"slot": 2, "type": {"name": "poison", "url": "https://pokeapi.co/api/v2/type/4/"}},
            ],
            "abilities": [
                {
                    "is_hidden": False,
                    "slot": 1,
                    "ability": {"name": "overgrow", "url": "https://pokeapi.co/api/v2/ability/65/"},
                },
                {
                    "is_hidden": True,
                    "slot": 3,
                    "ability": {"name": "chlorophyll", "url": "https://pokeapi.co/api/v2/ability/34/"},
                },
            ],
            "stats": [
                {"base_stat": 45, "effort": 0, "stat": {"name": "hp", "url": "https://pokeapi.co/api/v2/stat/1/"}},
                {
                    "base_stat": 49,
                    "effort": 0,
                    "stat": {"name": "attack", "url": "https://pokeapi.co/api/v2/stat/2/"},
                },
            ],
        }
        client = PokemonClient(rate_limit_per_sec=1000, concurrency=10)
        with patch.object(httpx.AsyncClient, "get", return_value=_MockResponse(payload)):
            p = await client.fetch_pokemon(1)

        assert p.id == 1
        assert p.name == "bulbasaur"
        assert p.height == 7
        assert p.weight == 69
        assert p.base_experience == 64
        assert [t.name for t in p.types] == ["grass", "poison"]
        assert [a.name for a in p.abilities] == ["overgrow", "chlorophyll"]
        assert [(s.name, s.base_stat) for s in p.stats] == [("hp", 45), ("attack", 49)]


class TestIntegration:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fetch_pokemon_from_api(self):
        """Real API connectivity + parsing (integration)."""
        client = PokemonClient(rate_limit_per_sec=3, concurrency=2)
        pokemon = await client.fetch_pokemon(1)

        assert pokemon.id == 1
        assert pokemon.name.lower() == "bulbasaur"
        assert pokemon.height > 0
        assert pokemon.weight > 0
        assert isinstance(pokemon.types, list)
        assert isinstance(pokemon.abilities, list)
        assert isinstance(pokemon.stats, list)
