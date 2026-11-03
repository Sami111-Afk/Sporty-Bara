import json
import os
from datetime import datetime, timedelta, timezone

from sportybara.api_football import parse_fixtures
from sportybara.match_id import match_id
from sportybara.odds_api import parse_odds_events

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return json.load(f)


def test_format_id():
    kickoff = datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc)
    assert match_id("laliga", kickoff, "Barcelona", "Sevilla") == "laliga_20261108_barcelona_sevilla"


def test_id_in_utc_nu_in_ora_locala():
    # 00:30 în România (+02:00) pe 9 nov = 22:30 UTC pe 8 nov
    local = datetime(2026, 11, 9, 0, 30, tzinfo=timezone(timedelta(hours=2)))
    assert match_id("laliga", local, "Barcelona", "Sevilla") == "laliga_20261108_barcelona_sevilla"


def test_acelasi_meci_din_ambele_api_uri_are_acelasi_id():
    odds = parse_odds_events(_load("odds_laliga.json"), "laliga")
    fixtures = parse_fixtures(_load("fixtures_laliga.json"), "laliga")
    ids_odds = {m["matchId"] for m in odds}
    ids_fx = {m["matchId"] for m in fixtures}

    # Barcelona–Sevilla: același nume în ambele API-uri
    assert "laliga_20261108_barcelona_sevilla" in ids_odds & ids_fx
    # Atlético de Madrid (Odds) vs Atletico Madrid (API-Football): aliasuri
    assert "laliga_20261109_atletico-madrid_real-betis" in ids_odds
    assert "laliga_20261109_atletico-madrid_real-betis" in ids_fx
