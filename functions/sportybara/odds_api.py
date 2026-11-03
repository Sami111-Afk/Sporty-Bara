"""Transformarea răspunsului The Odds API v4 în meciuri și cote (fără Firebase)."""
from datetime import datetime

from sportybara.match_id import match_id
from sportybara.odds import OUTCOMES, best_odds


def _parse_time(value: str) -> datetime:
    # „2026-11-08T20:00:00Z” → datetime aware în UTC
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _bookmaker_odds(bookmaker: dict, home: str, away: str):
    """Cotele 1X2 ale unui bookmaker, sau None dacă lipsește vreun rezultat."""
    h2h = next((m for m in bookmaker.get("markets", []) if m.get("key") == "h2h"), None)
    if h2h is None:
        return None
    # în The Odds API, egalul are numele „Draw”, celelalte rezultate au numele echipelor
    names = {home: "home", away: "away", "Draw": "draw"}
    prices = {}
    for outcome in h2h.get("outcomes", []):
        key = names.get(outcome.get("name"))
        if key is not None:
            prices[key] = round(float(outcome["price"]), 2)
    if set(prices) != set(OUTCOMES):
        return None
    return prices


def parse_odds_events(events: list, league: str) -> list:
    """Evenimentele din API → [{matchId, match, odds}], gata de scris în Firestore.

    odds: {bookmaker: {home, draw, away}}. Bookmakerii incompleți se ignoră,
    evenimentele fără niciun bookmaker valid se sar.
    """
    result = []
    for ev in events:
        home, away = ev["home_team"], ev["away_team"]
        odds = {}
        for bookmaker in ev.get("bookmakers", []):
            prices = _bookmaker_odds(bookmaker, home, away)
            if prices is not None:
                odds[bookmaker["key"]] = prices
        if not odds:
            continue

        kickoff = _parse_time(ev["commence_time"])
        result.append({
            "matchId": match_id(league, kickoff, home, away),
            "match": {
                "league": league,
                "home": home,
                "away": away,
                "kickoff": kickoff,
                "status": "scheduled",
                "bestOdds": best_odds(odds),
                "externalIds": {"oddsApi": ev["id"]},
            },
            "odds": odds,
        })
    return result
