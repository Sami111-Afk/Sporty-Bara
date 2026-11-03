"""Filtrul de relevanță: articolul trebuie să vorbească despre una din echipe."""

import re
from datetime import datetime

from .dedup import strip_diacritics
from .models import Article


def _mentions(text: str, name: str) -> bool:
    """Numele apare ca cuvânt întreg (fără diacritice, fără contare pe litere mici)."""
    pattern = r"\b" + re.escape(strip_diacritics(name).lower()) + r"\b"
    return re.search(pattern, strip_diacritics(text).lower()) is not None


def is_relevant(article: Article, home: str, away: str, since: datetime) -> bool:
    """True dacă articolul e recent și menționează una din echipe.

    `since` trebuie să fie cu fus orar (aware), ca și `article.published`.
    Articolul fără dată e considerat relevant.
    """
    if article.published is not None and article.published < since:
        return False
    text = f"{article.title} {article.summary}"
    return _mentions(text, home) or _mentions(text, away)
