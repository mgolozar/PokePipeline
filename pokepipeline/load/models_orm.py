"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import mapped_column, relationship

from pokepipeline.load.db import Base


class TimestampMixin:
    """Mixin for timestamp columns."""

    created_at = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Pokemon(Base, TimestampMixin):
    """Pokemon table."""

    __tablename__ = "pokemon"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(255), nullable=False)
    height = mapped_column(Integer, nullable=True)
    weight = mapped_column(Integer, nullable=True)
    base_experience = mapped_column(Integer, nullable=True)
    height_m = mapped_column(Float, nullable=True)
    weight_kg = mapped_column(Float, nullable=True)
    base_stat_total = mapped_column(Integer, nullable=True)
    bulk_index = mapped_column(Float, nullable=True)

    types = relationship("PokemonType", back_populates="pokemon", cascade="all, delete-orphan")
    abilities = relationship("PokemonAbility", back_populates="pokemon", cascade="all, delete-orphan")
    stats = relationship("PokemonStat", back_populates="pokemon", cascade="all, delete-orphan")


class Type(Base, TimestampMixin):
    """Type table."""

    __tablename__ = "type"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False, unique=True, index=True)


class Ability(Base, TimestampMixin):
    """Ability table."""

    __tablename__ = "ability"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False, unique=True, index=True)


class Stat(Base, TimestampMixin):
    """Stat table."""

    __tablename__ = "stat"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False, unique=True, index=True)


class PokemonType(Base, TimestampMixin):
    """Pokemon-Type junction table."""

    __tablename__ = "pokemon_type"

    pokemon_id = mapped_column(Integer, ForeignKey("pokemon.id", ondelete="CASCADE"), primary_key=True)
    type_id = mapped_column(Integer, ForeignKey("type.id", ondelete="CASCADE"), primary_key=True)

    pokemon = relationship("Pokemon", back_populates="types")
    type = relationship("Type")


class PokemonAbility(Base, TimestampMixin):
    """Pokemon-Ability junction table."""

    __tablename__ = "pokemon_ability"

    pokemon_id = mapped_column(Integer, ForeignKey("pokemon.id", ondelete="CASCADE"), primary_key=True)
    ability_id = mapped_column(Integer, ForeignKey("ability.id", ondelete="CASCADE"), primary_key=True)
    is_hidden = mapped_column(Boolean, nullable=False, default=False)
    slot = mapped_column(Integer, nullable=True)

    pokemon = relationship("Pokemon", back_populates="abilities")
    ability = relationship("Ability")


class PokemonStat(Base, TimestampMixin):
    """Pokemon-Stat junction table."""

    __tablename__ = "pokemon_stat"

    pokemon_id = mapped_column(Integer, ForeignKey("pokemon.id", ondelete="CASCADE"), primary_key=True)
    stat_id = mapped_column(Integer, ForeignKey("stat.id", ondelete="CASCADE"), primary_key=True)
    base_value = mapped_column(Integer, nullable=False)
    effort = mapped_column(Integer, nullable=False)

    pokemon = relationship("Pokemon", back_populates="stats")
    stat = relationship("Stat")
