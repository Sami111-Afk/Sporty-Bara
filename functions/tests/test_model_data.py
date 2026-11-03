import os
from datetime import date

from sportybara.model import data

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


def test_format_main_sp1():
    ms = data.parse_csv_text(read("sp1_sample.csv"))
    # meciul fără scor e ignorat
    assert [(m["home"], m["away"]) for m in ms] == [("Almeria", "Vallecano"), ("Betis", "Sevilla")]
    a, b = ms
    assert a["date"] == date(2023, 8, 11) and (a["hg"], a["ag"]) == (0, 2)
    # preferă cotele de închidere (AvgC*/MaxC*)
    assert a["odds_avg"] == {"home": 2.5, "draw": 3.1, "away": 2.8}
    assert a["odds_max"] == {"home": 2.6, "draw": 3.2, "away": 2.9}
    # fără cote de închidere → cele de deschidere
    assert b["odds_avg"]["home"] == 2.1 and b["odds_max"]["away"] == 3.8


def test_format_new_rou_cu_bom():
    ms = data.parse_csv_text(read("rou_sample.csv"))
    assert len(ms) == 2  # meciul din viitor (fără scor) e ignorat
    a, b = ms
    assert a["season"] == "2012/2013" and a["date"] == date(2012, 7, 20)
    assert a["home"] == "Pandurii" and (a["hg"], a["ag"]) == (6, 2)
    assert a["odds_avg"] == {"home": 1.47, "draw": 3.85, "away": 6.43}
    assert a["odds_max"]["home"] == 1.55
    # cote medii lipsă → None, dar cele max există
    assert b["odds_avg"] is None and b["odds_max"]["away"] == 1.86


def test_detect_format_si_data():
    assert data.detect_format(["HomeTeam", "AwayTeam"]) == "main"
    assert data.detect_format(["Home", "Away", "Season"]) == "new"
    assert data.parse_date("05/03/24") == date(2024, 3, 5)
