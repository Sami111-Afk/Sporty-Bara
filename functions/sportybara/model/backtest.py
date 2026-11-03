"""Backtest walk-forward: la fiecare etapă (bloc de zile) modelele văd DOAR meciurile de dinainte."""
import bisect
import math
from datetime import timedelta

from ..odds import OUTCOMES, fair_probabilities
from .combine import combine, fair_odds
from .elo import EloModel
from .poisson import PoissonModel

# ponderi fixate a priori (nu optimizate pe datele de test)
W_MODEL = {"poisson": 0.65, "elo": 0.35}                      # fără piață
W_ALL = {"poisson": 0.35, "elo": 0.15, "market": 0.50}        # cu piața
PRODUCTS = ("poisson", "elo", "model", "all", "market")
THRESHOLDS = (0.0, 0.05, 0.10, 0.20)


def outcome_of(m: dict) -> str:
    return "home" if m["hg"] > m["ag"] else "draw" if m["hg"] == m["ag"] else "away"


def walk_forward(matches, test_start, xi=None, block_days: int = 7, min_train: int = 150, elo_kwargs=None):
    """Predicții pentru toate meciurile cu data >= test_start.

    Pentru fiecare bloc (meciuri la < block_days de la primul), Poisson și Elo se
    antrenează doar pe meciuri cu data STRICT mai mică decât începutul blocului.
    Întoarce [{match, outcome, probs: {poisson, elo, model, all, market?}}].
    """
    matches = sorted(matches, key=lambda m: m["date"])
    dates = [m["date"] for m in matches]
    elo = EloModel(**(elo_kwargs or {}))
    elo_done = 0
    out = []
    i = bisect.bisect_left(dates, test_start)
    while i < len(matches):
        start = dates[i]
        end = bisect.bisect_left(dates, start + timedelta(days=block_days))
        train_end = bisect.bisect_left(dates, start)  # doar meciuri < start
        for m in matches[elo_done:train_end]:
            elo.update(m["home"], m["away"], m["hg"], m["ag"])
        elo_done = train_end
        if train_end >= min_train:
            elo.calibrate()
            pm = PoissonModel(**({"xi": xi} if xi is not None else {})).fit(matches[:train_end], start)
            for m in matches[i:end]:
                probs = {
                    "poisson": pm.predict(m["home"], m["away"]),
                    "elo": elo.predict(m["home"], m["away"]),
                }
                probs["model"] = combine([probs["poisson"], probs["elo"]],
                                         [W_MODEL["poisson"], W_MODEL["elo"]])
                if m["odds_avg"]:
                    probs["market"] = fair_probabilities(m["odds_avg"])
                    probs["all"] = combine([probs["poisson"], probs["elo"], probs["market"]],
                                           [W_ALL["poisson"], W_ALL["elo"], W_ALL["market"]])
                else:
                    probs["all"] = probs["model"]
                out.append({"match": m, "outcome": outcome_of(m), "probs": probs})
        i = end
    return out


def metrics(records, product: str) -> dict:
    """log loss, Brier (suma pătratelor pe cele 3 rezultate) și acuratețe; doar meciurile cu cote de piață."""
    rows = [r for r in records if "market" in r["probs"]]
    n = len(rows)
    ll = br = acc = 0.0
    for r in rows:
        p = r["probs"][product]
        ll += -math.log(max(p[r["outcome"]], 1e-12))
        br += sum((p[k] - (1.0 if k == r["outcome"] else 0.0)) ** 2 for k in OUTCOMES)
        acc += max(OUTCOMES, key=lambda k: p[k]) == r["outcome"]
    return {"n": n, "log_loss": ll / n, "brier": br / n, "accuracy": acc / n} if n else {"n": 0}


def value_bets(records, product: str = "model", thresholds=THRESHOLDS) -> list:
    """Pariu de 1 unitate pe fiecare rezultat unde cota MAX din piață > cota noastră × (1 + prag)."""
    res = []
    for thr in thresholds:
        n = wins = 0
        profit = 0.0
        for r in records:
            mx = r["match"]["odds_max"]
            if not mx or "market" not in r["probs"]:
                continue
            fair = fair_odds(r["probs"][product])
            for k in OUTCOMES:
                if mx[k] > fair[k] * (1 + thr):
                    n += 1
                    if k == r["outcome"]:
                        wins += 1
                        profit += mx[k] - 1
                    else:
                        profit -= 1
        res.append({"threshold": thr, "bets": n, "wins": wins, "profit": profit,
                    "roi": profit / n if n else None})
    return res


def baseline_all_bets(records) -> dict:
    """Referință: pariu pe toate cele 3 rezultate la cota MAX (ROI-ul „orb”)."""
    n = 0
    profit = 0.0
    for r in records:
        mx = r["match"]["odds_max"]
        if not mx or "market" not in r["probs"]:
            continue
        for k in OUTCOMES:
            n += 1
            profit += (mx[k] - 1) if k == r["outcome"] else -1
    return {"bets": n, "profit": profit, "roi": profit / n if n else None}


def run(matches, test_start, **kw) -> dict:
    """Rulează walk-forward + toate metricile pentru o ligă."""
    records = walk_forward(matches, test_start, **kw)
    return {
        "records": records,
        "metrics": {p: metrics(records, p) for p in PRODUCTS},
        "value": {p: value_bets(records, p) for p in ("model", "all")},
        "baseline": baseline_all_bets(records),
    }
