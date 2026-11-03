import pytest

from sportybara.teams import canonical, slug


@pytest.mark.parametrize("name, expected", [
    ("Atlético de Madrid", "atletico-de-madrid"),
    ("Alavés", "alaves"),
    ("Atl. Madrid", "atl-madrid"),
    ("Sevilla", "sevilla"),
])
def test_slug_scoate_diacritice_si_punctuatie(name, expected):
    assert slug(name) == expected


def test_slug_nu_scoate_prefixe_fc_cf_cfr():
    # prefixele rămân: „CFR Cluj” nu trebuie confundat cu „Cluj”
    assert slug("FC Barcelona") == "fc-barcelona"
    assert slug("CFR Cluj") == "cfr-cluj"


@pytest.mark.parametrize("name, expected", [
    ("Atletico Madrid", "atletico-madrid"),
    ("Atlético de Madrid", "atletico-madrid"),
    ("Atl. Madrid", "atletico-madrid"),
    ("Athletic Bilbao", "athletic-bilbao"),
    ("Athletic Club", "athletic-bilbao"),
    ("Real Betis", "real-betis"),
    ("Betis", "real-betis"),
    ("Celta Vigo", "celta-vigo"),
    ("Celta de Vigo", "celta-vigo"),
    ("Deportivo Alaves", "alaves"),
    ("Alavés", "alaves"),
    ("Barcelona", "barcelona"),
])
def test_canonical_aplica_aliasurile(name, expected):
    assert canonical(name) == expected
