"""Pydantic models for PokeAPI responses."""

from pydantic import BaseModel


class TypeRef(BaseModel):
    name: str


class AbilityRef(BaseModel):
    name: str


class StatRef(BaseModel):
    name: str
    base_stat: int


class PokemonAPIModel(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    base_experience: int
    types: list[TypeRef]
    abilities: list[AbilityRef]
    stats: list[StatRef]


class SpeciesAPIModel(BaseModel):
    id: int
    name: str
    evolution_chain_url: str | None = None


class EvolutionChainAPIModel(BaseModel):
    id: int
    chain: dict
