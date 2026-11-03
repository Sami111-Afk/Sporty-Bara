import pytest

from sportybara.odds import best_odds, fair_probabilities, margin

ODDS = {"home": 1.80, "draw": 3.60, "away": 4.50}


def test_margin_positive():
    assert margin(ODDS) == pytest.approx(1 / 1.8 + 1 / 3.6 + 1 / 4.5 - 1)
    assert margin(ODDS) > 0


def test_fair_probabilities_sum_to_one():
    probs = fair_probabilities(ODDS)
    assert sum(probs.values()) == pytest.approx(1)
    assert probs["home"] > probs["draw"] > probs["away"]


def test_best_odds_picks_highest_per_outcome():
    books = {
        "a": {"home": 1.80, "draw": 3.60, "away": 4.50},
        "b": {"home": 1.85, "draw": 3.50, "away": 4.40},
        "c": {"home": 1.75, "draw": 3.70, "away": 4.60},
    }
    best = best_odds(books)
    assert best["home"] == {"odd": 1.85, "bookmaker": "b"}
    assert best["draw"] == {"odd": 3.70, "bookmaker": "c"}
    assert best["away"] == {"odd": 4.60, "bookmaker": "c"}
