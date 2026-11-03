"""Căutările Google News per meci."""

# cuvinte cheie în limba presei fiecărei ligi
LEAGUE_KEYWORDS = {
    "laliga": ("es", ["lesión", "baja", "alineación probable", "convocatoria", "sanción"]),
    "superliga": ("ro", ["accidentare", "accidentat", "echipa probabilă", "suspendat"]),
}

# căutările în engleză merg pentru ambele ligi
EN_KEYWORDS = ["injury", "team news"]


def build_queries(home: str, away: str, league: str) -> list[tuple[str, str]]:
    """Listă de (query, limbă) pentru un meci, fără duplicate."""
    if league not in LEAGUE_KEYWORDS:
        raise ValueError(f"ligă necunoscută: {league}")
    lang, keywords = LEAGUE_KEYWORDS[league]

    queries: list[tuple[str, str]] = []
    for team in (home, away):
        for kw in keywords:
            queries.append((f"{team} {kw}", lang))
        for kw in EN_KEYWORDS:
            queries.append((f"{team} {kw}", "en"))

    # arbitrul: căutare pe ambele echipe
    referee = "árbitro" if lang == "es" else "arbitru"
    queries.append((f"{referee} {home} {away}", lang))

    # păstrăm ordinea, scoatem dublurile
    unique: list[tuple[str, str]] = []
    for item in queries:
        if item not in unique:
            unique.append(item)
    return unique
