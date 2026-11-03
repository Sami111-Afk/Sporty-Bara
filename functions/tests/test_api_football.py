import json
import os
from datetime import date, datetime, timezone

import pytest

from sportybara.api_football import parse_fixtures, season_for

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _fixtures():
    with open(os.path.join(FIXTURES, "fixtures_laliga.json"), encoding="utf-8") as f:
        return json.load(f)


def _by_fixture_id(parsed, fixture_id):
    return next(m for m in parsed if m["update"]["externalIds"]["apiFootball"] == fixture_id)


def test_season_iulie_decembrie_ianuarie():
    assert season_for(date(2026, 7, 1)) == 2026
    assert season_for(date(2026, 12, 15)) == 2026
    assert season_for(date(2027, 1, 10)) == 2026
    assert season_for(date(2026, 6, 30)) == 2025


def test_season_accepta_si_datetime():
    assert season_for(datetime(2026, 11, 3, tzinfo=timezone.utc)) == 2026


def test_mapari_status_din_fixture():
    parsed = parse_fixtures(_fixtures(), "laliga")
    assert _by_fixture_id(parsed, 1208021)["update"]["status"] == "scheduled"  # NS
    assert _by_fixture_id(parsed, 1208022)["update"]["status"] == "live"       # 1H
    assert _by_fixture_id(parsed, 1207990)["update"]["status"] == "finished"   # FT
    assert _by_fixture_id(parsed, 1208030)["update"]["status"] == "scheduled"  # PST
    assert _by_fixture_id(parsed, 1208040)["update"]["status"] == "cancelled"  # CANC


@pytest.mark.parametrize("short, expected", [
    ("NS", "scheduled"), ("TBD", "scheduled"), ("PST", "scheduled"),
    ("1H", "live"), ("HT", "live"), ("2H", "live"), ("ET", "live"), ("BT", "live"),
    ("P", "live"), ("LIVE", "live"), ("INT", "live"), ("SUSP", "live"),
    ("FT", "finished"), ("AET", "finished"), ("PEN", "finished"), ("AWD", "finished"), ("WO", "finished"),
    ("CANC", "cancelled"), ("ABD", "cancelled"),
    ("XYZ", "scheduled"),  # necunoscut → scheduled
])
def test_toate_codurile_de_status(short, expected):
    payload = {"response": [{
        "fixture": {"id": 1, "date": "2026-11-08T20:00:00+00:00", "status": {"short": short}},
        "teams": {"home": {"name": "A"}, "away": {"name": "B"}},
        "goals": {"home": 1, "away": 0},
    }]}
    assert parse_fixtures(payload, "laliga")[0]["update"]["status"] == expected


def test_score_none_pentru_meci_nepornit():
    parsed = parse_fixtures(_fixtures(), "laliga")
    assert _by_fixture_id(parsed, 1208021)["update"]["score"] is None
    assert _by_fixture_id(parsed, 1208030)["update"]["score"] is None


def test_score_pentru_meci_in_desfasurare_si_terminat():
    parsed = parse_fixtures(_fixtures(), "laliga")
    assert _by_fixture_id(parsed, 1208022)["update"]["score"] == {"home": 1, "away": 0}
    assert _by_fixture_id(parsed, 1207990)["update"]["score"] == {"home": 2, "away": 2}


def test_match_id_si_identitate_pentru_creare():
    parsed = parse_fixtures(_fixtures(), "laliga")
    item = _by_fixture_id(parsed, 1208021)
    assert item["matchId"] == "laliga_20261108_barcelona_sevilla"
    assert item["match"] == {
        "league": "laliga",
        "home": "Barcelona",
        "away": "Sevilla",
        "kickoff": datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc),
    }
    assert item["update"]["externalIds"] == {"apiFootball": 1208021}
