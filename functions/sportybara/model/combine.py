"""Combinarea probabilităților și verdictul față de cota casei."""
from ..odds import OUTCOMES


def combine(prob_list, weights) -> dict:
    """Medie ponderată a mai multor {home, draw, away}; ponderile se normalizează, rezultatul însumează 1."""
    total_w = sum(weights)
    if total_w <= 0:
        raise ValueError("ponderi invalide")
    out = {k: sum(w * p[k] for p, w in zip(prob_list, weights)) / total_w for k in OUTCOMES}
    s = sum(out.values())
    return {k: v / s for k, v in out.items()}


def fair_odds(probs: dict) -> dict:
    """Cota proprie = 1 / probabilitate."""
    return {k: 1 / probs[k] for k in OUTCOMES}


def verdict(market_odd: float, fair_odd: float, tolerance: float = 0.05) -> str:
    """„low”: cota casei e cu > tolerance sub cota noastră (o dă prea mică);
    „high”: cu > tolerance peste; altfel „fair”."""
    eps = 1e-9  # să nu depindă de rotunjiri la limită
    if market_odd < fair_odd * (1 - tolerance) - eps:
        return "low"
    if market_odd > fair_odd * (1 + tolerance) + eps:
        return "high"
    return "fair"
