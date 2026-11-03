"""Cloud Functions Sporty-Bara (Python).

Fiecare funcție nouă se adaugă aici; logica pură (fără Firebase) stă în pachetul
`sportybara/` ca să poată fi testată cu pytest fără emulator.
Contractul (parametri, răspunsuri, erori) e în docs/API.md.
"""
from datetime import datetime, timezone

import requests
from firebase_admin import firestore, initialize_app
from firebase_functions import https_fn, options, scheduler_fn
from firebase_functions.params import SecretParam

from sportybara.api_football import parse_fixtures, season_for
from sportybara.config import LEAGUES
from sportybara.http import get_json
from sportybara.odds_api import parse_odds_events

options.set_global_options(region="europe-west1", max_instances=5)
initialize_app()

ODDS_API_KEY = SecretParam("ODDS_API_KEY")
API_FOOTBALL_KEY = SecretParam("API_FOOTBALL_KEY")

ODDS_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"
FIXTURES_URL = "https://v3.football.api-sports.io/fixtures"
BATCH_MAX = 500  # limita Firestore pentru operații într-un batch


@https_fn.on_call()
def ping(req: https_fn.CallableRequest) -> dict:
    """Verificare că app-ul ajunge la funcții (folosit la legarea app ↔ Firebase)."""
    return {"ok": True, "uid": req.auth.uid if req.auth else None}


def _commit(db, ops):
    """Scrie [(referință, date)] cu merge, în batch-uri de cel mult BATCH_MAX."""
    for i in range(0, len(ops), BATCH_MAX):
        batch = db.batch()
        for ref, data in ops[i:i + BATCH_MAX]:
            batch.set(ref, data, merge=True)
        batch.commit()


@scheduler_fn.on_schedule(schedule="0 */6 * * *", secrets=[ODDS_API_KEY])
def fetch_odds(event: scheduler_fn.ScheduledEvent) -> None:
    """Aduce cotele 1X2 pentru ligile cu The Odds API → matches + matches/odds."""
    db = firestore.client()
    session = requests.Session()
    ops = []
    for league, ids in LEAGUES.items():
        if ids["oddsApi"] is None:
            continue
        events = get_json(
            session,
            ODDS_URL.format(sport=ids["oddsApi"]),
            params={"apiKey": ODDS_API_KEY.value(), "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
        )
        parsed = parse_odds_events(events, league)
        refs = [db.collection("matches").document(m["matchId"]) for m in parsed]
        existing = {snap.id for snap in db.get_all(refs) if snap.exists} if refs else set()

        for m, ref in zip(parsed, refs):
            match = dict(m["match"])
            # statusul îl pune fetch_results (live/finished); nu-l resetăm la „scheduled”
            if m["matchId"] in existing:
                match.pop("status")
            match["updatedAt"] = firestore.SERVER_TIMESTAMP
            ops.append((ref, match))
            for bookmaker, prices in m["odds"].items():
                ops.append((ref.collection("odds").document(bookmaker),
                            {**prices, "updatedAt": firestore.SERVER_TIMESTAMP}))
    _commit(db, ops)


@scheduler_fn.on_schedule(schedule="*/30 * * * *", secrets=[API_FOOTBALL_KEY])
def fetch_results(event: scheduler_fn.ScheduledEvent) -> None:
    """Aduce statusul și scorul din API-Football. Superliga (fără cote) își creează documentele."""
    db = firestore.client()
    session = requests.Session()
    season = season_for(datetime.now(timezone.utc))
    ops = []
    for league, ids in LEAGUES.items():
        payload = get_json(
            session,
            FIXTURES_URL,
            params={"league": ids["apiFootball"], "season": season},
            headers={"x-apisports-key": API_FOOTBALL_KEY.value()},
        )
        parsed = parse_fixtures(payload, league)
        refs = [db.collection("matches").document(m["matchId"]) for m in parsed]
        snaps = {snap.id: snap for snap in db.get_all(refs)} if refs else {}

        for m, ref in zip(parsed, refs):
            snap = snaps[m["matchId"]]
            if snap.exists:
                ops.append((ref, {**m["update"], "updatedAt": firestore.SERVER_TIMESTAMP}))
            elif ids["oddsApi"] is None:
                # fără cote: creăm meciul aici, cu câmpurile de identitate și bestOdds gol
                ops.append((ref, {**m["match"], **m["update"], "bestOdds": {},
                                  "updatedAt": firestore.SERVER_TIMESTAMP}))
            # pentru ligile cu cote, meciul apare doar prin fetch_odds
    _commit(db, ops)
