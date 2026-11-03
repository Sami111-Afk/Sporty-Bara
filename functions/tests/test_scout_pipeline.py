import os
from datetime import datetime, timedelta, timezone

import requests

from sportybara.scout.extract import FakeExtractor
from sportybara.scout.models import Factor
from sportybara.scout.pending import to_pending_docs
from sportybara.scout.pipeline import collect, run
from sportybara.scout.queries import build_queries
from sportybara.scout.rss import FEEDS

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "scout")
SINCE = datetime(2000, 1, 1, tzinfo=timezone.utc)
MATCH = {"id": "m1", "home": "Barcelona", "away": "Arsenal", "league": "laliga"}


def _read(name: str) -> bytes:
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


class FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self):
        pass


class FixtureSession:
    """Google News primește fixture-ul Google, BBC fixture-ul BBC, restul un feed gol."""

    def __init__(self):
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append(url)
        if "news.google.com" in url:
            return FakeResponse(_read("google_news.xml"))
        if "bbci.co.uk" in url:
            return FakeResponse(_read("press_bbc.xml"))
        return FakeResponse(b"<rss version='2.0'><channel></channel></rss>")


class FailingSession:
    def get(self, url, headers=None, timeout=None):
        raise requests.ConnectionError("fără rețea")


def _factor(**overrides):
    data = dict(
        type="injury",
        team="home",
        player="Raphinha",
        playProbability=0.0,
        effect={"home": -0.03},
        source="DAZN",
        url="https://ex.com/raphinha",
        date=datetime(2026, 11, 1, 10, 0),
    )
    data.update(overrides)
    return Factor(**data)


def test_to_pending_docs_fields_and_status():
    docs = to_pending_docs("m1", [_factor()])
    assert len(docs) == 1
    doc = docs[0]
    assert doc["matchId"] == "m1"
    assert doc["status"] == "pending"
    assert doc["type"] == "injury"
    assert doc["player"] == "Raphinha"
    assert doc["effect"] == {"home": -0.03}
    assert set(doc) == {
        "type", "team", "player", "playProbability", "effect",
        "source", "url", "date", "matchId", "status",
    }


def test_to_pending_docs_date_is_utc():
    naive = to_pending_docs("m1", [_factor(date=datetime(2026, 11, 1, 10, 0))])[0]
    assert naive["date"] == datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)

    plus_two = timezone(timedelta(hours=2))
    aware = to_pending_docs("m1", [_factor(date=datetime(2026, 11, 1, 12, 0, tzinfo=plus_two))])[0]
    assert aware["date"] == datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)
    assert aware["date"].utcoffset() == timedelta(0)


def test_collect_makes_one_request_per_query_and_feed():
    session = FixtureSession()
    collect(session, MATCH, SINCE, delay=0)
    expected = len(build_queries("Barcelona", "Arsenal", "laliga")) + len(FEEDS)
    assert len(session.calls) == expected


def test_collect_returns_relevant_deduplicated_articles():
    articles = collect(FixtureSession(), MATCH, SINCE, delay=0)
    urls = [a.url for a in articles]
    # fiecare căutare întoarce aceleași 4 articole: trebuie să rămână o singură dată
    assert len(urls) == len(set(urls))
    # știrile Google despre Barcelona sunt relevante, cele de presă doar dacă citează o echipă
    assert sum(1 for a in articles if a.source == "DAZN") == 1
    assert not any("Tenerife" in a.title for a in articles)
    # „Saliba's back for Arsenal” e din fluxul BBC și menționează Arsenal
    bbc = [a for a in articles if a.source == "BBC Sport"]
    assert len(bbc) == 1
    assert "Saliba" in bbc[0].title


def test_collect_survives_network_errors():
    assert collect(FailingSession(), MATCH, SINCE, delay=0) == []


def test_run_turns_factors_into_pending_docs():
    extractor = FakeExtractor([_factor()])
    docs = run(FixtureSession(), MATCH, extractor, SINCE, delay=0)
    articles = collect(FixtureSession(), MATCH, SINCE, delay=0)
    # un apel de extragere per articol, un document per factor
    assert len(extractor.calls) == len(articles)
    assert len(docs) == len(articles)
    assert all(d["matchId"] == "m1" and d["status"] == "pending" for d in docs)
    # extractorul primește echipele din meci
    assert extractor.calls[0][1:] == ("Barcelona", "Arsenal")
