"""HTTP client for PokeAPI."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from pokepipeline.extract.models_api import (
    AbilityRef,
    PokemonAPIModel,
    StatRef,
    TypeRef,
)

BASE_URL = "https://pokeapi.co/api/v2"


def _extract_pokemon_id(url: str) -> int | None:
    """Extract pokemon ID from URL."""
    try:
        parts = url.rstrip("/").split("/")
        return int(parts[-1])
    except (ValueError, IndexError):
        return None


def _safe_get(data: dict, *keys: str) -> Any:
    """Safely get nested dict value."""
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


class PokemonClient:
    def __init__(
        self,
        *,
        timeout: int = 10,
        rate_limit_per_sec: int = 5,
        concurrency: int = 5,
    ) -> None:
        self.timeout = timeout
        self.rate_limit_per_sec = max(1, rate_limit_per_sec)
        self.concurrency = max(1, concurrency)
        self._min_interval = 1.0 / self.rate_limit_per_sec
        self._last_request = 0.0
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(self.concurrency)

    async def _get(self, url: str) -> httpx.Response:
        """Make HTTP GET request with rate limiting and retries."""
        for attempt in range(3):
            await self._rate_limit_wait()
            
            async with self._semaphore:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        resp = await client.get(url)
                        resp.raise_for_status()
                        return resp
                except httpx.HTTPError:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.5 * (attempt + 1))
    
    async def _rate_limit_wait(self) -> None:
        """Wait to maintain rate limit."""
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_request
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            self._last_request = time.time()

    async def fetch_pokemon_ids(self, limit: int, offset: int) -> list[int]:
        """Fetch list of pokemon IDs."""
        url = f"{BASE_URL}/pokemon?limit={limit}&offset={offset}"
        resp = await self._get(url)
        data = resp.json()

        ids = []
        for item in data.get("results", []):
            if not isinstance(item, dict):
                continue
            pokemon_id = _extract_pokemon_id(item.get("url", ""))
            if pokemon_id is not None:
                ids.append(pokemon_id)

        return sorted(ids)

    def _parse_refs(self, items: list[dict], key: str) -> list[str]:
        names = []
        for item in items:
            name = _safe_get(item, key, "name")
            if name:
                names.append(name)
        return names

    async def fetch_pokemon(self, pokemon_id: int) -> PokemonAPIModel:
        """Fetch pokemon details by ID."""
        url = f"{BASE_URL}/pokemon/{pokemon_id}/"
        resp = await self._get(url)
        data = resp.json()

        type_names = self._parse_refs(data.get("types", []), "type")
        types = [TypeRef(name=name) for name in type_names]

        ability_names = self._parse_refs(data.get("abilities", []), "ability")
        abilities = [AbilityRef(name=name) for name in ability_names]

        stats = []
        for item in data.get("stats", []):
            name = _safe_get(item, "stat", "name")
            if name:
                stats.append(StatRef(name=name, base_stat=item.get("base_stat", 0)))

        return PokemonAPIModel(
            id=data["id"],
            name=data["name"],
            height=data.get("height", 0),
            weight=data.get("weight", 0),
            base_experience=data.get("base_experience", 0),
            types=types,
            abilities=abilities,
            stats=stats,
        )


