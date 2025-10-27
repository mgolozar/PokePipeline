"""Repository for loading data into the database with idempotent UPSERTs."""

from __future__ import annotations

import logging
from typing import Any, Protocol

from sqlalchemy import inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from pokepipeline.load.db import Base
from pokepipeline.load.models_orm import (
    Ability,
    Pokemon,
    PokemonAbility,
    PokemonStat,
    PokemonType,
    Stat,
    Type,
)

logger = logging.getLogger(__name__)


class LoadBatchProtocol(Protocol):
    """Protocol describing LoadBatch structure."""

    @property
    def pokemons(self) -> list:
        """List of PokemonDTO objects."""

    @property
    def types(self) -> list:
        """List of TypeDTO objects."""

    @property
    def abilities(self) -> list:
        """List of AbilityDTO objects."""

    @property
    def stats(self) -> list:
        """List of StatDTO objects."""

    @property
    def pokemon_types(self) -> list:
        """List of PokemonTypeLink objects."""

    @property
    def pokemon_abilities(self) -> list:
        """List of PokemonAbilityLink objects."""

    @property
    def pokemon_stats(self) -> list:
        """List of PokemonStatLink objects."""


class RepositoryError(Exception):
    """Repository operation error."""

    pass


class Repository:
    """Repository for idempotent data loading."""

    def __init__(self, engine: Engine):
        """Initialize with database engine."""
        if engine is None:
            raise RepositoryError("Database engine cannot be None")
        self.engine = engine
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create missing tables if they don't exist."""
        try:
            insp = inspect(self.engine)
            existing = set(insp.get_table_names(schema="public"))

            required_tables = {
                Pokemon.__tablename__,
                Type.__tablename__,
                Ability.__tablename__,
                Stat.__tablename__,
                PokemonType.__tablename__,
                PokemonAbility.__tablename__,
                PokemonStat.__tablename__,
            }

            missing = required_tables - existing
            if not missing:
                return

            model_table_map = {
                Pokemon.__tablename__: Pokemon.__table__,
                Type.__tablename__: Type.__table__,
                Ability.__tablename__: Ability.__table__,
                Stat.__tablename__: Stat.__table__,
                PokemonType.__tablename__: PokemonType.__table__,
                PokemonAbility.__tablename__: PokemonAbility.__table__,
                PokemonStat.__tablename__: PokemonStat.__table__,
            }

            tables_to_create = [model_table_map[name] for name in missing]
            Base.metadata.create_all(bind=self.engine, tables=tables_to_create)
            logger.info(f"Created missing tables: {sorted(missing)}")

        except Exception as e:
            logger.warning(f"Could not ensure schema: {e}")

    def load_batch(self, lb: LoadBatchProtocol) -> dict[str, Any]:
        """Upsert a LoadBatch into the database.

        Returns:
            Dictionary with metrics about the operation
        """
        metrics = {
            "upserted_pokemon": 0,
            "inserted_types": 0,
            "inserted_abilities": 0,
            "inserted_stats": 0,
            "inserted_links": {"types": 0, "abilities": 0, "stats": 0},
        }

        if not lb or not lb.pokemons:
            logger.warning("Empty LoadBatch, skipping")
            return metrics

        pokemon_dto = lb.pokemons[0]
        pokemon_id = pokemon_dto.id

        try:
            with self.engine.begin() as conn:
                self._upsert_pokemon(conn, pokemon_dto, metrics)
                self._upsert_dimensions(conn, lb, metrics)
                
                type_map, ability_map, stat_map = self._build_dimension_maps(conn)
                self._insert_links(conn, lb, pokemon_id, type_map, ability_map, stat_map, metrics)
                
                logger.info(
                    f"Load batch completed: pokemon={pokemon_id}, "
                    f"types={metrics['inserted_links']['types']}, "
                    f"abilities={metrics['inserted_links']['abilities']}, "
                    f"stats={metrics['inserted_links']['stats']}"
                )

        except IntegrityError as e:
            raise RepositoryError(f"Database integrity violation for pokemon {pokemon_id}: {e}") from e
        except SQLAlchemyError as e:
            raise RepositoryError(f"Database operation failed for pokemon {pokemon_id}: {e}") from e

        return metrics

    def _upsert_pokemon(self, conn, pokemon_dto, metrics: dict) -> None:
        """Upsert pokemon data."""
        values = {
            "id": pokemon_dto.id,
            "name": pokemon_dto.name,
            "height": pokemon_dto.height,
            "weight": pokemon_dto.weight,
            "base_experience": pokemon_dto.base_experience,
        }
        
        if hasattr(pokemon_dto, 'height_m'):
            values["height_m"] = pokemon_dto.height_m
        if hasattr(pokemon_dto, 'weight_kg'):
            values["weight_kg"] = pokemon_dto.weight_kg
        if hasattr(pokemon_dto, 'base_stat_total'):
            values["base_stat_total"] = pokemon_dto.base_stat_total
        if hasattr(pokemon_dto, 'bulk_index'):
            values["bulk_index"] = pokemon_dto.bulk_index
            
        stmt = insert(Pokemon).values(**values)
        update_dict = {
            "name": stmt.excluded.name,
            "height": stmt.excluded.height,
            "weight": stmt.excluded.weight,
            "base_experience": stmt.excluded.base_experience,
        }
        
        if hasattr(pokemon_dto, 'height_m'):
            update_dict["height_m"] = stmt.excluded.height_m
        if hasattr(pokemon_dto, 'weight_kg'):
            update_dict["weight_kg"] = stmt.excluded.weight_kg
        if hasattr(pokemon_dto, 'base_stat_total'):
            update_dict["base_stat_total"] = stmt.excluded.base_stat_total
        if hasattr(pokemon_dto, 'bulk_index'):
            update_dict["bulk_index"] = stmt.excluded.bulk_index
            
        stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=update_dict)
        conn.execute(stmt)
        metrics["upserted_pokemon"] = 1

    def _upsert_dimensions(self, conn, lb: LoadBatchProtocol, metrics: dict) -> None:
        """Upsert dimension tables."""
        if lb.types:
            type_names = [t.name for t in lb.types]
            stmt = insert(Type).values([{"name": name} for name in type_names])
            stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
            metrics["inserted_types"] = conn.execute(stmt).rowcount or 0

        if lb.abilities:
            ability_names = [a.name for a in lb.abilities]
            stmt = insert(Ability).values([{"name": name} for name in ability_names])
            stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
            metrics["inserted_abilities"] = conn.execute(stmt).rowcount or 0

        if lb.stats:
            stat_names = [s.name for s in lb.stats]
            stmt = insert(Stat).values([{"name": name} for name in stat_names])
            stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
            metrics["inserted_stats"] = conn.execute(stmt).rowcount or 0

    def _build_dimension_maps(self, conn) -> tuple[dict, dict, dict]:
        """Build name->id maps for dimensions."""
        type_map = {name: id_ for name, id_ in conn.execute(select(Type.name, Type.id)).fetchall()}
        ability_map = {name: id_ for name, id_ in conn.execute(select(Ability.name, Ability.id)).fetchall()}
        stat_map = {name: id_ for name, id_ in conn.execute(select(Stat.name, Stat.id)).fetchall()}
        return type_map, ability_map, stat_map

    def _insert_links(self, conn, lb: LoadBatchProtocol, pokemon_id: int, 
                     type_map: dict, ability_map: dict, stat_map: dict, metrics: dict) -> None:
        """Insert linking tables for pokemon relationships."""
        if lb.pokemon_types:
            self._insert_type_links(conn, lb, pokemon_id, type_map, metrics)
        if lb.pokemon_abilities:
            self._insert_ability_links(conn, lb, pokemon_id, ability_map, metrics)
        if lb.pokemon_stats:
            self._insert_stat_links(conn, lb, pokemon_id, stat_map, metrics)

    def _insert_type_links(self, conn, lb: LoadBatchProtocol, pokemon_id: int, 
                          type_map: dict, metrics: dict) -> None:
        """Insert pokemon_type links."""
        type_links = []
        for link in lb.pokemon_types:
            if link.type_name in type_map:
                type_links.append({"pokemon_id": pokemon_id, "type_id": type_map[link.type_name]})
        
        if type_links:
            stmt = insert(PokemonType).values(type_links)
            stmt = stmt.on_conflict_do_nothing(index_elements=["pokemon_id", "type_id"])
            metrics["inserted_links"]["types"] = conn.execute(stmt).rowcount or 0

    def _insert_ability_links(self, conn, lb: LoadBatchProtocol, pokemon_id: int, 
                             ability_map: dict, metrics: dict) -> None:
        """Insert pokemon_ability links."""
        ability_links = []
        for link in lb.pokemon_abilities:
            if link.ability_name in ability_map:
                ability_links.append({
                    "pokemon_id": pokemon_id,
                    "ability_id": ability_map[link.ability_name],
                    "is_hidden": link.is_hidden,
                    "slot": link.slot,
                })
        
        if ability_links:
            stmt = insert(PokemonAbility).values(ability_links)
            stmt = stmt.on_conflict_do_nothing(index_elements=["pokemon_id", "ability_id"])
            metrics["inserted_links"]["abilities"] = conn.execute(stmt).rowcount or 0

    def _insert_stat_links(self, conn, lb: LoadBatchProtocol, pokemon_id: int, 
                          stat_map: dict, metrics: dict) -> None:
        """Insert pokemon_stat links."""
        stat_links = []
        for link in lb.pokemon_stats:
            if link.stat_name in stat_map:
                stat_links.append({
                    "pokemon_id": pokemon_id,
                    "stat_id": stat_map[link.stat_name],
                    "base_value": link.base_value,
                    "effort": link.effort,
                })
        
        if stat_links:
            stmt = insert(PokemonStat).values(stat_links)
            stmt = stmt.on_conflict_do_nothing(index_elements=["pokemon_id", "stat_id"])
            metrics["inserted_links"]["stats"] = conn.execute(stmt).rowcount or 0
