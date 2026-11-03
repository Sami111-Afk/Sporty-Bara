"""Unealtă de dezvoltare: rulează colectarea Scout LIVE și afișează articolele.

Exemplu:
    python tools/scout_cli.py --home Barcelona --away Sevilla --league laliga --days 3
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

# importă pachetul `sportybara` din functions/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sportybara.scout.pipeline import collect  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Scout: caută știri pentru un meci")
    parser.add_argument("--home", required=True, help="echipa gazdă")
    parser.add_argument("--away", required=True, help="echipa oaspete")
    parser.add_argument("--league", required=True, choices=["laliga", "superliga"])
    parser.add_argument("--days", type=int, default=3, help="câte zile în urmă (implicit 3)")
    parser.add_argument("--delay", type=float, default=1.0, help="pauză între cereri, secunde")
    args = parser.parse_args()

    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    match = {"id": None, "home": args.home, "away": args.away, "league": args.league}

    with requests.Session() as session:
        articles = collect(session, match, since, delay=args.delay)

    print(f"{len(articles)} articole din ultimele {args.days} zile\n")
    for a in articles:
        when = a.published.strftime("%Y-%m-%d %H:%M") if a.published else "fără dată"
        print(f"- {a.title}")
        print(f"  sursă: {a.source} | {when} UTC")
        print(f"  {a.url}")


if __name__ == "__main__":
    main()
