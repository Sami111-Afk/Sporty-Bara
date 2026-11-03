"""Cereri HTTP către API-urile externe. Sesiunea vine din afară, ca să poată fi falsă în teste."""


def get_json(session, url, params=None, headers=None, timeout=15):
    """GET și întoarce JSON-ul; ridică excepție la eroare HTTP (ex. limită de cereri depășită)."""
    r = session.get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()
