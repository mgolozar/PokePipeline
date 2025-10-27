"""Async HTTP client for PokeAPI."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Coroutine

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from pokepipeline.extract.models_api import (
    PokemonAPIModel,
    SpeciesAPIModel,
    EvolutionChainAPIModel,
    TypeRef,
    AbilityRef,
    StatRef,
)

BASE_URL = "https://pokeapi.co/api/v2"


class PokemonClient:
    """HTTP client for fetching Pokemon data with rate limiting and retries."""

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

    async def _wait_if_needed(self) -> None:
        """Enforces minimum time between requests."""
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_request
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            self._last_request = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    )
    async def _get(self, url: str) -> httpx.Response:
        """Fetch URL with rate limiting, concurrency control, and automatic retries."""
        await self._wait_if_needed()
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp

    async def fetch_pokemon_ids(self, limit: int, offset: int) -> list[int]:
        """Fetch Pokemon IDs for pagination."""
        url = f"{BASE_URL}/pokemon?limit={limit}&offset={offset}"
        resp = await self._get(url)
        data = resp.json()

        ids = []
        for item in data.get("results", []):
            try:
                url_path = item["url"].rstrip("/")
                pokemon_id = int(url_path.split("/")[-1])
                ids.append(pokemon_id)
            except (KeyError, ValueError):
                continue

        return sorted(ids)

    async def fetch_pokemon(self, pokemon_id: int) -> PokemonAPIModel:
        """Fetch Pokemon by ID."""
        url = f"{BASE_URL}/pokemon/{pokemon_id}/"
        resp = await self._get(url)
        data = resp.json()

        types = [
            TypeRef(name=t.get("type", {}).get("name", ""))
            for t in data.get("types", [])
        ]
        abilities = [
            AbilityRef(name=a.get("ability", {}).get("name", ""))
            for a in data.get("abilities", [])
        ]
        stats = [
            StatRef(name=s.get("stat", {}).get("name", ""), base_stat=s.get("base_stat", 0))
            for s in data.get("stats", [])
        ]

        return PokemonAPIModel(
            id=data["id"],
            name=data["name"],
            height=data["height"],
            weight=data["weight"],
            base_experience=data["base_experience"],
            types=types,
            abilities=abilities,
            stats=stats,
        )

    async def fetch_species(self, species_id: int) -> SpeciesAPIModel:
        """Fetch species data including evolution chain URL."""
        url = f"{BASE_URL}/pokemon-species/{species_id}/"
        resp = await self._get(url)
        data = resp.json()

        evo_chain = data.get("evolution_chain", {})
        evo_url = evo_chain.get("url") if isinstance(evo_chain, dict) else None

        return SpeciesAPIModel(
            id=data["id"],
            name=data["name"],
            evolution_chain_url=evo_url,
        )

    async def fetch_evolution_chain(self, chain_id: int) -> EvolutionChainAPIModel:
        """Fetch evolution chain data."""
        url = f"{BASE_URL}/evolution-chain/{chain_id}/"
        resp = await self._get(url)
        data = resp.json()

        return EvolutionChainAPIModel(id=data["id"], chain=data.get("chain", {}))


async def gather_limited(
    coros: list[Coroutine[Any, Any, Any]],
    concurrency: int,
) -> list[Any]:
    """Run coroutines with bounded concurrency."""
    if not coros:
        return []

    sem = asyncio.Semaphore(max(1, concurrency))

    async def _limited_run(coro: Coroutine[Any, Any, Any]) -> Any:
        async with sem:
            return await coro

    return list(await asyncio.gather(*(_limited_run(c) for c in coros)))
