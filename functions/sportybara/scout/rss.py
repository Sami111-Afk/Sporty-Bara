"""Aducerea și parsarea fluxurilor RSS (Google News + presă sportivă)."""

import calendar
import html
import logging
import re
import time
from datetime import datetime, timezone
from urllib.parse import quote

import feedparser

from .models import Article

log = logging.getLogger(__name__)

USER_AGENT = "SportyBaraScout/0.1 (proiect de facultate)"

# limba → (hl, gl) pentru Google News
GOOGLE_LOCALES = {
    "es": ("es", "ES"),
    "ro": ("ro", "RO"),
    "en": ("en-GB", "GB"),
}

# fluxuri fixe ale presei sportive, verificate pe 03-11-2026: RSS valid și articole
# de azi. GSP are /rss.xml (/rss și /feed dau 404). AS a fost scos: fluxurile
# as.com/rss/tags/ultimas_noticias.xml și futbol/primera.xml au articole doar din 2022-2024.
FEEDS = [
    ("Marca", "https://e00-marca.uecdn.es/rss/futbol/primera-division.xml"),
    ("Mundo Deportivo", "https://www.mundodeportivo.com/feed/rss/home"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/football/rss.xml"),
    ("GSP", "https://www.gsp.ro/rss.xml"),
]


def google_news_url(query: str, lang: str) -> str:
    """URL-ul RSS Google News pentru o căutare în limba dată."""
    hl, gl = GOOGLE_LOCALES[lang]
    return (
        f"https://news.google.com/rss/search?q={quote(query, safe='')}"
        f"&hl={hl}&gl={gl}&ceid={gl}:{lang}"
    )


def fetch(session, url: str, delay: float = 1.0) -> bytes:
    """Descarcă un URL; așteaptă `delay` secunde înainte, ca să nu bombardăm site-urile.

    Ridică requests.RequestException la eroare (apelantul decide ce face).
    """
    time.sleep(delay)
    resp = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    return resp.content


def _published(entry) -> datetime | None:
    """Data articolului în UTC; None dacă feed-ul nu o are."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)


def _plain(text: str) -> str:
    """Scoate tag-urile HTML din rezumat și comprimă spațiile."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return " ".join(text.split())


def parse_feed(xml_bytes: bytes, source: str, query: str) -> list[Article]:
    """Transformă un feed RSS în articole.

    source: numele fluxului (folosit dacă articolul nu spune sursa).
    Google News pune sursa reală în `entry.source`, iar titlul are forma
    „Titlu - Sursă”; sufixul se scoate din titlu.
    """
    feed = feedparser.parse(xml_bytes)
    articles: list[Article] = []
    for entry in feed.entries:
        title = _plain(entry.get("title", ""))
        url = entry.get("link", "")
        if not title or not url:
            continue

        real_source = (entry.get("source") or {}).get("title")
        if real_source:
            suffix = f" - {real_source}"
            if title.endswith(suffix):
                title = title[: -len(suffix)]
        articles.append(
            Article(
                title=title,
                url=url,
                source=real_source or source,
                published=_published(entry),
                summary=_plain(entry.get("summary", "")),
                query=query,
            )
        )
    return articles
