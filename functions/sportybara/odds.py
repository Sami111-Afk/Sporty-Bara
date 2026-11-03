"""Calcule pe cote zecimale (fără Firebase)."""

OUTCOMES = ("home", "draw", "away")


def implied_probabilities(odds: dict) -> dict:
    """Probabilitățile „brute” din cote: 1 / cotă (suma lor > 1 din cauza marjei)."""
    return {k: 1 / odds[k] for k in OUTCOMES}


def margin(odds: dict) -> float:
    """Marja casei: cu cât suma probabilităților depășește 100%."""
    return sum(implied_probabilities(odds).values()) - 1


def fair_probabilities(odds: dict) -> dict:
    """Probabilități fără marjă (metoda proporțională): normalizate să însumeze 1."""
    raw = implied_probabilities(odds)
    total = sum(raw.values())
    return {k: p / total for k, p in raw.items()}


def best_odds(bookmakers: dict) -> dict:
    """Cea mai bună cotă pentru fiecare rezultat.

    bookmakers: {"betfair": {"home": 1.5, "draw": 4.2, "away": 6.0}, ...}
    → {"home": {"odd": 1.55, "bookmaker": "unibet"}, ...}
    """
    best = {}
    for name, odds in bookmakers.items():
        for k in OUTCOMES:
            if k not in best or odds[k] > best[k]["odd"]:
                best[k] = {"odd": odds[k], "bookmaker": name}
    return best
