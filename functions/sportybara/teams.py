"""Nume de echipe normalizate, ca același meci să aibă același ID din ambele API-uri."""
import re
import unicodedata

# variantă (slug) → slug canonic; completăm pe măsură ce apar diferențe între API-uri
ALIASES = {
    "atletico-madrid": "atletico-madrid",
    "atletico-de-madrid": "atletico-madrid",
    "atl-madrid": "atletico-madrid",
    "athletic-bilbao": "athletic-bilbao",
    "athletic-club": "athletic-bilbao",
    "real-betis": "real-betis",
    "betis": "real-betis",
    "celta-vigo": "celta-vigo",
    "celta-de-vigo": "celta-vigo",
    "alaves": "alaves",
    "deportivo-alaves": "alaves",
}


def slug(name: str) -> str:
    """„Atlético de Madrid” → „atletico-de-madrid”."""
    # scoatem diacriticele (é → e, ș → s)
    fara_diacritice = unicodedata.normalize("NFKD", name)
    fara_diacritice = "".join(c for c in fara_diacritice if not unicodedata.combining(c))
    # orice secvență de litere/cifre rămâne, restul (spații, puncte) devine „-”
    return re.sub(r"[^a-z0-9]+", "-", fara_diacritice.lower()).strip("-")


def canonical(name: str) -> str:
    """Slug-ul după aliasuri: aceeași echipă, același rezultat, indiferent de API."""
    s = slug(name)
    return ALIASES.get(s, s)
