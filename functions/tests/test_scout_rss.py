import os
from datetime import datetime, timezone

from sportybara.scout.rss import USER_AGENT, fetch, google_news_url, parse_feed

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "scout")


def _read(name: str) -> bytes:
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


class FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self):
        pass


class FakeSession:
    def __init__(self, content: bytes = b"<rss/>"):
        self.content = content
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "timeout": timeout})
        return FakeResponse(self.content)


def test_google_news_url_spanish_encodes_query():
    url = google_news_url("Barcelona lesión", "es")
    assert url == (
        "https://news.google.com/rss/search?q=Barcelona%20lesi%C3%B3n"
        "&hl=es&gl=ES&ceid=ES:es"
    )


def test_google_news_url_romanian():
    url = google_news_url("FCSB accidentare", "ro")
    assert "hl=ro&gl=RO&ceid=RO:ro" in url
    assert "q=FCSB%20accidentare" in url


def test_google_news_url_english_uses_gb():
    url = google_news_url("Barcelona injury", "en")
    assert "hl=en-GB&gl=GB&ceid=GB:en" in url


def test_parse_google_news_fixture():
    articles = parse_feed(_read("google_news.xml"), "Google News", "Barcelona lesión")
    assert len(articles) == 4
    first = articles[0]
    # sufixul „ - DAZN” a fost scos din titlu, sursa e cea reală
    assert first.title.startswith("Parte médico lesión Raphinha")
    assert not first.title.endswith("DAZN")
    assert first.source == "DAZN"
    assert first.url.startswith("https://news.google.com/rss/articles/")
    assert first.query == "Barcelona lesión"
    assert first.published == datetime(2026, 10, 29, 14, 59, 36, tzinfo=timezone.utc)
    # rezumatul HTML e curățat
    assert "<a" not in first.summary


def test_parse_press_fixture_uses_feed_name_as_source():
    articles = parse_feed(_read("press_bbc.xml"), "BBC Sport", "")
    assert len(articles) == 4
    assert all(a.source == "BBC Sport" for a in articles)
    assert articles[0].title.startswith("Tenerife striker")
    assert articles[0].published.tzinfo is not None


def test_parse_skips_entries_without_title_or_link():
    xml = b"""<?xml version="1.0"?><rss version="2.0"><channel>
      <item><title>Fara link</title></item>
      <item><link>https://ex.com/a</link></item>
      <item><title>Corect</title><link>https://ex.com/b</link></item>
    </channel></rss>"""
    articles = parse_feed(xml, "Test", "q")
    assert [a.title for a in articles] == ["Corect"]
    assert articles[0].published is None


def test_fetch_sends_user_agent_timeout_and_returns_content():
    session = FakeSession(b"<rss>ok</rss>")
    content = fetch(session, "https://ex.com/feed", delay=0)
    assert content == b"<rss>ok</rss>"
    call = session.calls[0]
    assert call["headers"]["User-Agent"] == USER_AGENT
    assert USER_AGENT == "SportyBaraScout/0.1 (proiect de facultate)"
    assert call["timeout"] == 15
