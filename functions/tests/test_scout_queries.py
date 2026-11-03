import pytest

from sportybara.scout.queries import build_queries


def test_laliga_queries_in_spanish_and_english():
    queries = build_queries("Barcelona", "Sevilla", "laliga")
    assert ("Barcelona lesión", "es") in queries
    assert ("Sevilla alineación probable", "es") in queries
    assert ("Barcelona injury", "en") in queries
    assert ("Sevilla team news", "en") in queries
    assert ("árbitro Barcelona Sevilla", "es") in queries
    # în limba ligii, nu în română
    assert not any(lang == "ro" for _, lang in queries)


def test_superliga_queries_in_romanian_and_english():
    queries = build_queries("FCSB", "CFR Cluj", "superliga")
    assert ("FCSB accidentare", "ro") in queries
    assert ("CFR Cluj echipa probabilă", "ro") in queries
    assert ("FCSB injury", "en") in queries
    assert ("arbitru FCSB CFR Cluj", "ro") in queries
    assert not any(lang == "es" for _, lang in queries)


def test_no_duplicate_queries():
    queries = build_queries("Barcelona", "Sevilla", "laliga")
    assert len(queries) == len(set(queries))


def test_each_team_gets_all_keywords():
    queries = build_queries("Barcelona", "Sevilla", "laliga")
    for team in ("Barcelona", "Sevilla"):
        for kw in ("lesión", "baja", "alineación probable", "convocatoria", "sanción"):
            assert (f"{team} {kw}", "es") in queries


def test_unknown_league_raises():
    with pytest.raises(ValueError):
        build_queries("A", "B", "premier")
