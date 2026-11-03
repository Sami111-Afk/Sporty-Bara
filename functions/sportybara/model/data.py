"""Încărcare date istorice football-data.co.uk (doar biblioteca standard)."""
import csv
import io
import os
import urllib.request
from datetime import date, datetime

# cache local (ignorat de git)
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".data")

LA_LIGA_URL = "https://www.football-data.co.uk/mmz4281/{season}/SP1.csv"
ROMANIA_URL = "https://www.football-data.co.uk/new/ROU.csv"

# Fișierele „main” (SP1) și „new” (ROU) au coloane diferite.
# La ambele preferăm cotele de ÎNCHIDERE (AvgC*/MaxC*), apoi cele de deschidere.
_FORMATS = {
    "main": {
        "home": "HomeTeam", "away": "AwayTeam", "hg": "FTHG", "ag": "FTAG",
        "avg": [("AvgCH", "AvgCD", "AvgCA"), ("AvgH", "AvgD", "AvgA")],
        "max": [("MaxCH", "MaxCD", "MaxCA"), ("MaxH", "MaxD", "MaxA")],
    },
    "new": {
        "home": "Home", "away": "Away", "hg": "HG", "ag": "AG",
        "avg": [("AvgCH", "AvgCD", "AvgCA")],
        "max": [("MaxCH", "MaxCD", "MaxCA")],
    },
}


def detect_format(fieldnames) -> str:
    """„main” dacă are HomeTeam/AwayTeam, „new” dacă are Home/Away."""
    names = set(fieldnames or [])
    if "HomeTeam" in names:
        return "main"
    if "Home" in names and "Away" in names:
        return "new"
    raise ValueError("format CSV necunoscut")


def parse_date(text: str) -> date:
    """Datele sunt dd/mm/yyyy (la fișierele vechi și dd/mm/yy)."""
    text = text.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"dată invalidă: {text!r}")


def _odds(row: dict, candidates) -> dict | None:
    """Primul set de coloane complet și valid (cote > 1)."""
    for cols in candidates:
        try:
            vals = [float(row.get(c) or "") for c in cols]
        except ValueError:
            continue
        if all(v > 1 for v in vals):
            return dict(zip(("home", "draw", "away"), vals))
    return None


def parse_csv_text(text: str) -> list:
    """CSV → listă de meciuri normalizate, sortate după dată.

    Meci: {date, home, away, hg, ag, odds_avg, odds_max, season?}
    """
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    fmt = _FORMATS[detect_format(reader.fieldnames)]
    matches = []
    for row in reader:
        try:
            hg, ag = int(row[fmt["hg"]]), int(row[fmt["ag"]])
            d = parse_date(row["Date"])
        except (ValueError, KeyError, TypeError):
            continue  # rând gol sau meci fără scor (încă nejucat)
        home, away = (row[fmt["home"]] or "").strip(), (row[fmt["away"]] or "").strip()
        if not home or not away:
            continue
        m = {
            "date": d, "home": home, "away": away, "hg": hg, "ag": ag,
            "odds_avg": _odds(row, fmt["avg"]), "odds_max": _odds(row, fmt["max"]),
        }
        if row.get("Season"):
            m["season"] = row["Season"]
        matches.append(m)
    matches.sort(key=lambda m: m["date"])  # sortare stabilă
    return matches


def download(url: str, name: str, refresh: bool = False, cache_dir: str = CACHE_DIR) -> str:
    """Descarcă în cache (dacă nu există deja) și întoarce textul CSV."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, name)
    if refresh or not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": "sporty-bara-backtest"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


def load_la_liga(seasons, refresh: bool = False) -> list:
    """seasons: ex. ["2223", "2324"]."""
    out = []
    for s in seasons:
        out += parse_csv_text(download(LA_LIGA_URL.format(season=s), f"SP1_{s}.csv", refresh))
    out.sort(key=lambda m: m["date"])
    return out


def load_romania(refresh: bool = False) -> list:
    return parse_csv_text(download(ROMANIA_URL, "ROU.csv", refresh))
