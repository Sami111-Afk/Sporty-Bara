from datetime import datetime, timezone

from sportybara.scout.dedup import canonical_url, dedup, normalize_title
from sportybara.scout.models import Article


def _article(title, url, source="Test"):
    return Article(
        title=title,
        url=url,
        source=source,
        published=datetime(2026, 11, 1, tzinfo=timezone.utc),
        summary="",
        query="",
    )


def test_canonical_url_removes_tracking_params():
    url = "https://Ex.com/a/b?id=7&utm_source=x&fbclid=abc&gclid=def&utm_medium=y"
    assert canonical_url(url) == "https://ex.com/a/b?id=7"


def test_canonical_url_removes_fragment_and_trailing_slash():
    assert canonical_url("https://ex.com/stire/1/#comentarii") == "https://ex.com/stire/1"
    assert canonical_url("https://ex.com/stire/1/") == canonical_url("https://ex.com/stire/1")


def test_canonical_url_keeps_root_path_and_lowercases_host_only():
    assert canonical_url("HTTPS://WWW.Ex.com/") == "https://www.ex.com/"


def test_normalize_title_ignores_diacritics_case_and_punctuation():
    assert normalize_title("Lesión,   Raphinha!") == normalize_title("lesion raphinha")
    assert normalize_title("Echipă  probabilă") == "echipa probabila"


def test_dedup_same_url_with_tracking_keeps_first():
    articles = [
        _article("Titlu A", "https://ex.com/a?utm_source=x", "Primul"),
        _article("Alt titlu", "https://ex.com/a/", "Al doilea"),
    ]
    result = dedup(articles)
    assert len(result) == 1
    assert result[0].source == "Primul"


def test_dedup_same_title_with_different_diacritics():
    articles = [
        _article("Lesión de Raphinha confirmată", "https://a.com/1", "A"),
        _article("Lesion de Raphinha confirmata!", "https://b.com/2", "B"),
    ]
    result = dedup(articles)
    assert [a.source for a in result] == ["A"]


def test_dedup_keeps_different_articles():
    articles = [
        _article("Primul articol", "https://a.com/1"),
        _article("Al doilea articol", "https://a.com/2"),
    ]
    assert len(dedup(articles)) == 2
