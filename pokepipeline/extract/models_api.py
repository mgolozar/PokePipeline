"""Pydantic models for PokeAPI responses."""

from pydantic import BaseModel, ConfigDict


_MODEL_CONFIG = ConfigDict(extra="forbid")


class TypeRef(BaseModel):
    model_config = _MODEL_CONFIG
    name: str


class AbilityRef(BaseModel):
    model_config = _MODEL_CONFIG
    name: str


class StatRef(BaseModel):
    model_config = _MODEL_CONFIG
    name: str
    base_stat: int


class PokemonAPIModel(BaseModel):
    model_config = _MODEL_CONFIG
    
    id: int
    name: str
    height: int
    weight: int
    base_experience: int
    types: list[TypeRef]
    abilities: list[AbilityRef]
    stats: list[StatRef]
