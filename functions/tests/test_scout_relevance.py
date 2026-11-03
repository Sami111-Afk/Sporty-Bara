from datetime import datetime, timedelta, timezone

from sportybara.scout.models import Article
from sportybara.scout.relevance import is_relevant

NOW = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)
SINCE = NOW - timedelta(days=3)


def _article(title, summary="", published=NOW):
    return Article(
        title=title,
        url="https://ex.com/x",
        source="Test",
        published=published,
        summary=summary,
        query="",
    )


def test_relevant_when_title_mentions_home_team():
    assert is_relevant(_article("Barcelona, lesión de Raphinha"), "Barcelona", "Sevilla", SINCE)


def test_relevant_when_only_summary_mentions_away_team():
    article = _article("Parte médico", summary="El Sevilla recupera a su delantero")
    assert is_relevant(article, "Barcelona", "Sevilla", SINCE)


def test_diacritics_are_ignored_in_match():
    article = _article("Atletico Madrid: baja confirmada")
    assert is_relevant(article, "Atlético Madrid", "Getafe", SINCE)


def test_team_name_must_be_whole_word():
    # „Real” nu trebuie să se potrivească în „Realizare”
    assert not is_relevant(_article("Realizare fără precedent"), "Real", "Getafe", SINCE)


def test_not_relevant_when_no_team_mentioned():
    assert not is_relevant(_article("Vremea din Madrid"), "Barcelona", "Sevilla", SINCE)


def test_old_article_is_not_relevant():
    old = _article("Barcelona lesión", published=SINCE - timedelta(days=1))
    assert not is_relevant(old, "Barcelona", "Sevilla", SINCE)


def test_article_without_date_is_relevant():
    undated = _article("Barcelona lesión", published=None)
    assert is_relevant(undated, "Barcelona", "Sevilla", SINCE)


def test_city_news_is_not_relevant():
    # „Barcelona” orașul, nu echipa
    assert not is_relevant(_article("El alquiler medio sube en Barcelona"), "Barcelona", "Sevilla", SINCE)


def test_both_teams_mentioned_is_relevant_without_keywords():
    assert is_relevant(_article("Barcelona y Sevilla, cara a cara"), "Barcelona", "Sevilla", SINCE)


def test_terms_match_at_word_start_only():
    # „golf” nu e „gol”, „medicina” nu e „médico”, „returned” nu e „return”
    assert not is_relevant(_article("Barcelona acoge un torneo de golf"), "Barcelona", "Sevilla", SINCE)
    assert not is_relevant(_article("Barcelona, capital de la medicina"), "Barcelona", "Sevilla", SINCE)
    assert not is_relevant(_article("Tourists returned to Barcelona"), "Barcelona", "Sevilla", SINCE)


def test_spanish_road_accident_is_not_football():
    assert not is_relevant(_article("Accidente de tráfico en Barcelona"), "Barcelona", "Sevilla", SINCE)


def test_injury_terms_still_match():
    assert is_relevant(_article("Lesión de Lewandowski: el Barcelona confirma la baja"), "Barcelona", "Sevilla", SINCE)
    assert is_relevant(_article("Barcelona: gol de Yamal en el entrenamiento"), "Barcelona", "Sevilla", SINCE)
    assert is_relevant(_article("FCSB: Olaru, accidentat"), "FCSB", "Rapid", SINCE)
