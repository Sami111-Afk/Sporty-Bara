"""Structuri de date pentru Scout (fără Firebase)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    """Un articol găsit de căutare sau de un flux RSS."""

    title: str
    url: str
    source: str
    published: datetime | None
    summary: str
    query: str


@dataclass
class Factor:
    """Un factor care poate modifica o cotă (ref. docs/API.md → factors)."""

    type: str
    team: str
    player: str | None
    playProbability: float | None
    effect: dict
    source: str
    url: str
    date: datetime
