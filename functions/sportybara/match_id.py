"""ID-ul unic al unui meci: același meci din Odds API și API-Football dă același ID."""
from datetime import datetime, timezone

from sportybara.teams import canonical


def match_id(league: str, kickoff: datetime, home: str, away: str) -> str:
    """ex. „laliga_20261108_barcelona_sevilla”. Data e cea UTC, ca să nu depindă de fus."""
    if kickoff.tzinfo is not None:
        kickoff = kickoff.astimezone(timezone.utc)
    return f"{league}_{kickoff:%Y%m%d}_{canonical(home)}_{canonical(away)}"
