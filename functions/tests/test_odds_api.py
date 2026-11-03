import json
import os
from datetime import datetime, timedelta, timezone

from sportybara.odds_api import parse_odds_events

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _events():
    with open(os.path.join(FIXTURES, "odds_laliga.json"), encoding="utf-8") as f:
        return json.load(f)


def _by_id(parsed, match_id):
    return next(m for m in parsed if m["matchId"] == match_id)


def test_best_odds_corecte():
    parsed = parse_odds_events(_events(), "laliga")
    m = _by_id(parsed, "laliga_20261108_barcelona_sevilla")["match"]
    # home: bet365 (1.50) > unibet (1.45); draw: unibet (4.6) > bet365 (4.4); away: unibet (6.5) > bet365 (6.0)
    assert m["bestOdds"] == {
        "home": {"odd": 1.5, "bookmaker": "bet365"},
        "draw": {"odd": 4.6, "bookmaker": "unibet_eu"},
        "away": {"odd": 6.5, "bookmaker": "unibet_eu"},
    }


def test_bookmaker_incomplet_e_ignorat():
    parsed = parse_odds_events(_events(), "laliga")
    m = _by_id(parsed, "laliga_20261108_barcelona_sevilla")
    # betfair_ex_eu n-are egal, deci nu intră nici în cote, nici în best odds (ar fi avut 1.9 la home)
    assert set(m["odds"]) == {"unibet_eu", "bet365"}
    assert m["match"]["bestOdds"]["home"]["odd"] == 1.5


def test_eveniment_fara_bookmaker_valid_e_sarit():
    parsed = parse_odds_events(_events(), "laliga")
    assert len(parsed) == 3
    assert all("Girona" not in m["match"]["home"] for m in parsed)


def test_kickoff_utc_aware():
    parsed = parse_odds_events(_events(), "laliga")
    kickoff = _by_id(parsed, "laliga_20261108_barcelona_sevilla")["match"]["kickoff"]
    assert kickoff == datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc)
    assert kickoff.utcoffset() == timedelta(0)


def test_campuri_match_si_odds():
    parsed = parse_odds_events(_events(), "laliga")
    m = _by_id(parsed, "laliga_20261109_atletico-madrid_real-betis")
    assert m["match"]["league"] == "laliga"
    assert m["match"]["home"] == "Atlético de Madrid"
    assert m["match"]["away"] == "Real Betis"
    assert m["match"]["status"] == "scheduled"
    assert m["match"]["externalIds"] == {"oddsApi": "7c1a0f3e9b2d4e6f8a1b3c5d7e9f0a1b"}
    assert m["odds"]["bet365"] == {"home": 2.05, "draw": 3.4, "away": 3.7}


def test_id_alias_pentru_athletic_club():
    parsed = parse_odds_events(_events(), "laliga")
    assert "laliga_20261109_athletic-bilbao_celta-vigo" in {m["matchId"] for m in parsed}
