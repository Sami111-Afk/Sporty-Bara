"""Interfața de extragere a factorilor din articole.

Extractorul real va folosi un model de limbaj cu ieșire structurată și se
adaugă separat. Aici avem doar interfața și un extractor fals pentru teste.
"""

from typing import Protocol

from .models import Article, Factor


class Extractor(Protocol):
    def extract(self, article: Article, home: str, away: str) -> list[Factor]:
        """Întoarce factorii citați de articol (lista poate fi goală)."""
        ...


class FakeExtractor:
    """Întoarce mereu aceiași factori; păstrează apelurile pentru verificare în teste."""

    def __init__(self, factors: list[Factor]):
        self.factors = list(factors)
        self.calls: list[tuple[Article, str, str]] = []

    def extract(self, article: Article, home: str, away: str) -> list[Factor]:
        self.calls.append((article, home, away))
        return list(self.factors)
