"""Pydantic v2 DTO models for data transformation and loading."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


_STRICT_CONFIG = ConfigDict(extra="forbid")


class PokemonDTO(BaseModel):
    model_config = _STRICT_CONFIG

    id: int
    name: str
    height: int | None = None
    weight: int | None = None
    base_experience: int | None = None
    height_m: float | None = None
    weight_kg: float | None = None
    base_stat_total: int | None = None
    bulk_index: float | None = None


class TypeDTO(BaseModel):
    model_config = _STRICT_CONFIG

    id: int | None = None
    name: str


class AbilityDTO(BaseModel):
    model_config = _STRICT_CONFIG

    id: int | None = None
    name: str


class StatDTO(BaseModel):
    model_config = _STRICT_CONFIG

    id: int | None = None
    name: str


class PokemonTypeLink(BaseModel):
    model_config = _STRICT_CONFIG

    pokemon_id: int
    type_name: str


class PokemonAbilityLink(BaseModel):
    model_config = _STRICT_CONFIG

    pokemon_id: int
    ability_name: str
    is_hidden: bool
    slot: int | None = None


class PokemonStatLink(BaseModel):
    model_config = _STRICT_CONFIG

    pokemon_id: int
    stat_name: str
    base_value: int
    effort: int


class LoadBatch(BaseModel):
    model_config = _STRICT_CONFIG

    pokemons: list[PokemonDTO]
    types: list[TypeDTO]
    abilities: list[AbilityDTO]
    stats: list[StatDTO]
    pokemon_types: list[PokemonTypeLink]
    pokemon_abilities: list[PokemonAbilityLink]
    pokemon_stats: list[PokemonStatLink]
