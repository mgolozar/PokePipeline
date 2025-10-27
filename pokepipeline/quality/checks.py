"""Quality checks for LoadBatch validation."""

from __future__ import annotations

import logging

from pokepipeline.transform.models_dto import LoadBatch

logger = logging.getLogger(__name__)

REQUIRED_STATS = {"hp", "attack", "defense", "special-attack", "special-defense", "speed"}


def ensure_required_stats(lb: LoadBatch) -> tuple[bool, str | None]:
    """Check if LoadBatch contains all required stats."""
    collected_stats = {s.name for s in lb.stats}
    missing = REQUIRED_STATS - collected_stats

    if missing:
        reason = f"missing required stats: {sorted(missing)}"
        logger.warning("LoadBatch validation failed: %s", reason)
        return False, reason

    return True, None


def ensure_has_type(lb: LoadBatch) -> tuple[bool, str | None]:
    """Check if LoadBatch has at least one type."""
    if not lb.types:
        reason = "no types found"
        logger.warning("LoadBatch validation failed: %s", reason)
        return False, reason

    return True, None


def validate_loadbatch(lb: LoadBatch) -> tuple[bool, list[str]]:
    """Validate LoadBatch against all quality checks."""
    reasons = []

    is_valid, reason = ensure_required_stats(lb)
    if not is_valid:
        reasons.append(reason)

    is_valid, reason = ensure_has_type(lb)
    if not is_valid:
        reasons.append(reason)

    is_valid = len(reasons) == 0
    return is_valid, reasons
