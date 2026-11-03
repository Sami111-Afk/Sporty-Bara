"""Lanțul Scout: căutare → RSS → relevanță → deduplicare → factori → pending."""

import logging
from datetime import datetime

import requests

from .dedup import dedup
from .extract import Extractor
from .models import Article
from .pending import to_pending_docs
from .queries import build_queries
from .relevance import is_relevant
from .rss import FEEDS, fetch, google_news_url, parse_feed

log = logging.getLogger(__name__)


def collect(session, match: dict, since: datetime, delay: float = 1.0) -> list[Article]:
    """Articolele relevante pentru meci, fără dubluri.

    match: {"id", "home", "away", "league"}. `since` trebuie să fie aware (UTC).
    Erorile de rețea la un flux sunt doar logate, nu opresc restul.
    """
    home, away = match["home"], match["away"]
    articles: list[Article] = []

    for query, lang in build_queries(home, away, match["league"]):
        try:
            content = fetch(session, google_news_url(query, lang), delay)
        except requests.RequestException as exc:
            log.warning("Google News eșuat pentru %r: %s", query, exc)
            continue
        articles += parse_feed(content, "Google News", query)

    for name, url in FEEDS:
        try:
            content = fetch(session, url, delay)
        except requests.RequestException as exc:
            log.warning("flux %s eșuat: %s", name, exc)
            continue
        articles += parse_feed(content, name, "")

    relevant = [a for a in articles if is_relevant(a, home, away, since)]
    return dedup(relevant)


def run(session, match: dict, extractor: Extractor, since: datetime, delay: float = 1.0) -> list[dict]:
    """collect + extragerea factorilor din fiecare articol → documente pending."""
    home, away = match["home"], match["away"]
    factors = []
    for article in collect(session, match, since, delay=delay):
        factors.extend(extractor.extract(article, home, away))
    return to_pending_docs(match["id"], factors)
