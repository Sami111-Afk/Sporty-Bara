"""Ligile urmărite și ID-urile lor în API-urile externe."""

LEAGUES = {
    "laliga": {"oddsApi": "soccer_spain_la_liga", "apiFootball": 140},
    # de verificat cu /v4/sports dacă The Odds API acoperă Superliga; până atunci fără cote
    "superliga": {"oddsApi": None, "apiFootball": 283},
}
