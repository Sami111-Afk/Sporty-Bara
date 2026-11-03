import random
from datetime import date, timedelta

import pytest

from sportybara.model import backtest
from sportybara.model.combine import combine, fair_odds, verdict
from sportybara.model.elo import EloModel
from sportybara.model.poisson import PoissonModel

TEAMS = {"Tare": 2.2, "Mediu1": 1.3, "Mediu2": 1.2, "Slab": 0.6}


def poisson_draw(rng, lam):
    # Poisson prin inversiune (fără numpy, seed fix)
    import math
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def synthetic(seed=1, rounds=40, start=date(2022, 8, 1), odds=True):
    """Campionat sintetic dus-întors; goluri ~ Poisson(forță gazdă / oaspete)."""
    rng = random.Random(seed)
    names = list(TEAMS)
    out, d = [], start
    for _ in range(rounds):
        for h in names:
            for a in names:
                if h == a:
                    continue
                hg = poisson_draw(rng, TEAMS[h] * 0.9 * 1.2)
                ag = poisson_draw(rng, TEAMS[a] * 0.9 / 1.0)
                m = {"date": d, "home": h, "away": a, "hg": hg, "ag": ag, "odds_avg": None, "odds_max": None}
                if odds:
                    m["odds_avg"] = {"home": 2.0, "draw": 3.4, "away": 4.0}
                    m["odds_max"] = {"home": 2.1, "draw": 3.6, "away": 4.2}
                out.append(m)
                d += timedelta(days=1)
    return out


def test_poisson_suma_1_si_echipa_tare_favorita():
    ms = synthetic(rounds=12)
    pm = PoissonModel().fit(ms, ms[-1]["date"] + timedelta(days=1))
    p = pm.predict("Tare", "Slab")
    assert sum(p.values()) == pytest.approx(1.0)
    assert p["home"] > p["away"] and p["home"] > 0.6
    q = pm.predict("Slab", "Tare")
    assert q["away"] > q["home"]
    assert sum(q.values()) == pytest.approx(1.0)


def test_poisson_echipa_necunoscuta_nu_crapa():
    ms = synthetic(rounds=6)
    pm = PoissonModel().fit(ms, ms[-1]["date"] + timedelta(days=1))
    assert sum(pm.predict("Necunoscut", "Tare").values()) == pytest.approx(1.0)


def test_poisson_ignora_meciurile_din_viitor():
    ms = synthetic(rounds=4)
    cutoff = ms[20]["date"]
    a = PoissonModel().fit(ms, cutoff).predict("Tare", "Slab")
    # schimbăm drastic rezultatele de după cutoff → predicția nu se schimbă
    alt = [dict(m, hg=9, ag=0) if m["date"] >= cutoff else m for m in ms]
    b = PoissonModel().fit(alt, cutoff).predict("Tare", "Slab")
    assert a == b


def test_elo_creste_dupa_victorie_si_suma_1():
    elo = EloModel()
    before_h, before_a = elo.rating("A"), elo.rating("B")
    elo.update("A", "B", 2, 0)
    assert elo.rating("A") > before_h and elo.rating("B") < before_a
    # zero-sum
    assert elo.rating("A") + elo.rating("B") == pytest.approx(before_h + before_a)
    assert sum(elo.predict("A", "B").values()) == pytest.approx(1.0)
    # după victorie, A e mai favorită față de un adversar nou decât înainte
    assert elo.predict("A", "C")["home"] > EloModel().predict("A", "C")["home"]


def test_elo_egal_intre_egali_si_calibrare():
    elo = EloModel()
    for m in synthetic(rounds=15):
        elo.update(m["home"], m["away"], m["hg"], m["ag"])
    elo.calibrate()
    assert elo.scale > 0 and elo.c > 0
    p = elo.predict("Tare", "Slab")
    assert p["home"] > p["away"] and sum(p.values()) == pytest.approx(1.0)


def test_combine_si_fair_odds():
    a = {"home": 0.5, "draw": 0.3, "away": 0.2}
    b = {"home": 0.3, "draw": 0.3, "away": 0.4}
    c = combine([a, b], [3, 1])
    assert sum(c.values()) == pytest.approx(1.0)
    assert c["home"] == pytest.approx(0.45)
    assert fair_odds(a)["home"] == pytest.approx(2.0)


def test_verdict_cazuri_limita():
    assert verdict(1.80, 2.00) == "low"     # 10% sub cota noastră
    assert verdict(2.20, 2.00) == "high"    # 10% peste
    assert verdict(2.00, 2.00) == "fair"
    assert verdict(1.90, 2.00) == "fair"    # exact -5% = încă fair
    assert verdict(2.10, 2.00) == "fair"    # exact +5% = încă fair
    assert verdict(1.89, 2.00) == "low"
    assert verdict(2.11, 2.00) == "high"
    assert verdict(1.39, 2.0, tolerance=0.30) == "low"
    assert verdict(1.45, 2.0, tolerance=0.30) == "fair"


def test_backtest_walk_forward_nu_foloseste_viitorul():
    ms = synthetic(rounds=12)
    start = ms[60]["date"]
    base = backtest.walk_forward(ms, start, min_train=30)
    assert base
    # răstorn rezultatele tuturor meciurilor de după mijlocul testului
    pivot = base[len(base) // 2]["match"]["date"]
    alt = [dict(m, hg=7, ag=0) if m["date"] > pivot else m for m in ms]
    other = backtest.walk_forward(alt, start, min_train=30)
    assert len(base) == len(other)
    checked = 0
    for r1, r2 in zip(base, other):
        # predicțiile pentru meciuri până la pivot nu depind de rezultate viitoare
        if r1["match"]["date"] <= pivot:
            assert r1["probs"]["poisson"] == r2["probs"]["poisson"]
            assert r1["probs"]["elo"] == r2["probs"]["elo"]
            checked += 1
    assert checked > 10


def test_backtest_metrici_si_value():
    ms = synthetic(rounds=6)
    res = backtest.run(ms, ms[60]["date"], min_train=30)
    for p in backtest.PRODUCTS:
        m = res["metrics"][p]
        assert m["n"] == len(res["records"])
        assert 0 < m["log_loss"] < 3 and 0 < m["brier"] < 2 and 0 <= m["accuracy"] <= 1
    for v in res["value"]["model"]:
        assert v["wins"] <= v["bets"]
    # praguri mai mari → mai puține pariuri
    bets = [v["bets"] for v in res["value"]["model"]]
    assert bets == sorted(bets, reverse=True)
