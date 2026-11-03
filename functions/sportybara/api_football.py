"""Transformarea răspunsului API-Football v3 în rezultate și statusuri (fără Firebase)."""
from datetime import datetime

from sportybara.match_id import match_id

# statusul API-Football → statusul din contract (docs/API.md)
STATUS = {
    "NS": "scheduled", "TBD": "scheduled", "PST": "scheduled",
    "1H": "live", "HT": "live", "2H": "live", "ET": "live", "BT": "live",
    "P": "live", "LIVE": "live", "INT": "live", "SUSP": "live",
    "FT": "finished", "AET": "finished", "PEN": "finished", "AWD": "finished", "WO": "finished",
    "CANC": "cancelled", "ABD": "cancelled",
}


def season_for(date) -> int:
    """Anul de START al sezonului: din iulie încoace, anul curent; altfel anul precedent."""
    return date.year if date.month >= 7 else date.year - 1


def parse_fixtures(payload: dict, league: str) -> list:
    """Meciurile din API → [{matchId, match, update}].

    update: status și score (None până începe meciul), plus externalIds.apiFootball.
    match: câmpurile de identitate, folosite doar când meciul nu există încă în Firestore.
    """
    result = []
    for item in payload.get("response", []):
        fx = item["fixture"]
        home = item["teams"]["home"]["name"]
        away = item["teams"]["away"]["name"]
        kickoff = datetime.fromisoformat(fx["date"].replace("Z", "+00:00"))
        status = STATUS.get((fx.get("status") or {}).get("short"), "scheduled")

        goals = item.get("goals") or {}
        score = None
        if status != "scheduled" and goals.get("home") is not None and goals.get("away") is not None:
            score = {"home": goals["home"], "away": goals["away"]}

        result.append({
            "matchId": match_id(league, kickoff, home, away),
            "match": {"league": league, "home": home, "away": away, "kickoff": kickoff},
            "update": {
                "status": status,
                "score": score,
                "externalIds": {"apiFootball": fx["id"]},
            },
        })
    return result
