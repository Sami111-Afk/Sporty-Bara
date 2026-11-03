"""Deduplicarea articolelor după URL canonic și după titlu."""

import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import Article

# parametri de urmărire adăugați de rețele și de reclame
TRACKING_EXACT = {"fbclid", "gclid"}
TRACKING_PREFIX = "utm_"


def strip_diacritics(text: str) -> str:
    """„Lesión” → „Lesion”."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def canonical_url(url: str) -> str:
    """URL fără parametri de urmărire, fragment și slash final; host în minuscule."""
    parts = urlsplit(url.strip())
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.startswith(TRACKING_PREFIX) and k not in TRACKING_EXACT
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), "")
    )


def normalize_title(title: str) -> str:
    """Titlu comparabil: fără diacritice, fără punctuație, litere mici, spații comprimate."""
    text = strip_diacritics(title).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def dedup(articles: list[Article]) -> list[Article]:
    """Scoate dublurile (același URL canonic sau același titlu normalizat).

    Păstrează primul articol văzut.
    """
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    result: list[Article] = []
    for article in articles:
        url_key = canonical_url(article.url)
        title_key = normalize_title(article.title)
        if url_key in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        seen_titles.add(title_key)
        result.append(article)
    return result
