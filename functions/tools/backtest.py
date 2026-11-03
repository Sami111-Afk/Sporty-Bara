"""Rulează backtest-ul walk-forward pe date reale (football-data.co.uk) și tipărește tabelele în Markdown.

Exemplu:  cd functions && .venv/bin/python tools/backtest.py --league all
"""
import argparse
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sportybara.model import backtest, data  # noqa: E402

LABELS = {"poisson": "Poisson", "elo": "Elo", "model": "Poisson+Elo", "all": "Combinat (cu piață)",
          "market": "Piață (cote medii, fără marjă)"}

LEAGUES = {
    # nume: (încărcare, început test)
    "laliga": ("La Liga", lambda a: data.load_la_liga(["2122", "2223", "2324", "2425", "2526", "2627"], a.refresh),
               date(2022, 8, 1)),
    "romania": ("Superliga România", lambda a: data.load_romania(a.refresh), date(2022, 7, 1)),
}


def season_of(d):
    """Anul de start al sezonului (iulie–iunie)."""
    return d.year if d.month >= 7 else d.year - 1


def print_league(name, res):
    recs = res["records"]
    n = res["metrics"]["market"]["n"]
    first, last = recs[0]["match"]["date"], recs[-1]["match"]["date"]
    print(f"\n### {name}: {n} meciuri evaluate ({first} – {last})\n")
    print("| Model | Log loss | Brier | Acuratețe |")
    print("|---|---|---|---|")
    for p in backtest.PRODUCTS:
        m = res["metrics"][p]
        print(f"| {LABELS[p]} | {m['log_loss']:.4f} | {m['brier']:.4f} | {m['accuracy'] * 100:.1f}% |")
    print("\nPe sezon (log loss; sezonul 2026/27 e parțial):\n")
    print("| Sezon | Meciuri | Poisson | Elo | Poisson+Elo | Combinat | Piață |")
    print("|---|---|---|---|---|---|---|")
    seasons = sorted({season_of(r["match"]["date"]) for r in recs})
    for s in seasons:
        sub = [r for r in recs if season_of(r["match"]["date"]) == s]
        ms = {p: backtest.metrics(sub, p) for p in backtest.PRODUCTS}
        print(f"| {s}/{s + 1} | {ms['market']['n']} | " + " | ".join(
            f"{ms[p]['log_loss']:.4f}" for p in ("poisson", "elo", "model", "all", "market")) + " |")
    b = res["baseline"]
    print(f"\nPariere „value” (1 unitate, cota MAX din piață > cota noastră × (1+prag)); "
          f"referință „toate rezultatele la cota max”: {b['bets']} pariuri, ROI {b['roi'] * 100:.1f}%\n")
    print("| Prag | Cota noastră din | Pariuri | Câștigate | Profit | ROI |")
    print("|---|---|---|---|---|---|")
    for p in ("model", "all"):
        for v in res["value"][p]:
            roi = "-" if v["roi"] is None else f"{v['roi'] * 100:.1f}%"
            print(f"| {v['threshold'] * 100:.0f}% | {LABELS[p]} | {v['bets']} | {v['wins']} | {v['profit']:.1f} | {roi} |")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--league", choices=["laliga", "romania", "all"], default="all")
    ap.add_argument("--refresh", action="store_true", help="redescarcă CSV-urile")
    ap.add_argument("--block-days", type=int, default=7)
    args = ap.parse_args()
    for key, (name, load, start) in LEAGUES.items():
        if args.league in ("all", key):
            res = backtest.run(load(args), start, block_days=args.block_days)
            print_league(name, res)


if __name__ == "__main__":
    main()
