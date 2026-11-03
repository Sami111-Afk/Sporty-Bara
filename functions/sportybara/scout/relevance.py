"""Filtrul de relevanță: articolul trebuie să vorbească despre una din echipe, ca echipă de fotbal."""

import re
from datetime import datetime

from .dedup import strip_diacritics
from .models import Article


def _mentions(text: str, name: str) -> bool:
    """Numele apare ca cuvânt întreg (fără diacritice, fără contare pe litere mici)."""
    pattern = r"\b" + re.escape(strip_diacritics(name).lower()) + r"\b"
    return re.search(pattern, strip_diacritics(text).lower()) is not None


# rădăcini de cuvinte din fotbal (fără diacritice); „Barcelona” singur prinde și știri
# despre oraș (vreme, chirii), așa că cerem și un context de fotbal sau ambele echipe
FOOTBALL_TERMS = (
    # es
    "lesi", "baja", "alinea", "convoca", "sanci", "arbitr", "titular", "entrenador",
    "partido", "jornada", "laliga", "gol", "delanter", "portero", "defensa", "medic",
    "recuper", "plantilla", "fichaje", "once ",
    # en
    "injur", "team news", "lineup", "line-up", "squad", "suspen", "ruled out", "doubt",
    "fitness", "coach", "manager", "match", "fixture", "striker", "goalkeeper",
    # ro
    "accident", "echip", "lotul", "meci", "antrenor", "fotbal", "superliga", "jucator",
    "atacant", "portar", "fundas", "transfer",
)


def _football_context(text: str) -> bool:
    norm = strip_diacritics(text).lower()
    return any(term in norm for term in FOOTBALL_TERMS)


def is_relevant(article: Article, home: str, away: str, since: datetime) -> bool:
    """True dacă articolul e recent, menționează una din echipe și e despre fotbal
    (menționează ambele echipe sau conține un termen din FOOTBALL_TERMS).

    `since` trebuie să fie cu fus orar (aware), ca și `article.published`.
    Articolul fără dată e considerat relevant.
    """
    if article.published is not None and article.published < since:
        return False
    text = f"{article.title} {article.summary}"
    home_hit, away_hit = _mentions(text, home), _mentions(text, away)
    if not (home_hit or away_hit):
        return False
    return (home_hit and away_hit) or _football_context(text)
