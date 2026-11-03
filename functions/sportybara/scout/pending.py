"""Transformarea factorilor în documente `pending_factors` (ref. docs/API.md)."""

from datetime import timezone

from .models import Factor

FACTOR_FIELDS = ("type", "team", "player", "playProbability", "effect", "source", "url", "date")


def to_pending_docs(match_id: str, factors: list[Factor]) -> list[dict]:
    """Câmpurile din `factors` + `matchId` + `status: "pending"`; data în UTC."""
    docs = []
    for factor in factors:
        doc = {field: getattr(factor, field) for field in FACTOR_FIELDS}
        # datele naive le considerăm deja UTC
        if doc["date"].tzinfo is None:
            doc["date"] = doc["date"].replace(tzinfo=timezone.utc)
        else:
            doc["date"] = doc["date"].astimezone(timezone.utc)
        doc["matchId"] = match_id
        doc["status"] = "pending"
        docs.append(doc)
    return docs
