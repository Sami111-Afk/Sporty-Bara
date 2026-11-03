"""Poisson tip Dixon–Coles simplificat: atac/apărare pe echipă + avantaj teren, cu ponderare în timp."""
import math

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import gammaln

# timp de înjumătățire ~ 1 sezon (365 zile)
DEFAULT_XI = math.log(2) / 365


def _tau(x, y, lh, la, rho):
    """Corecția Dixon–Coles pentru scoruri mici (0-0, 0-1, 1-0, 1-1)."""
    if x == 0 and y == 0:
        return 1 - lh * la * rho
    if x == 0 and y == 1:
        return 1 + lh * rho
    if x == 1 and y == 0:
        return 1 + la * rho
    if x == 1 and y == 1:
        return 1 - rho
    return 1.0


class PoissonModel:
    """log λ_gazdă = mu + h + atac[gazdă] − apărare[oaspete]; log λ_oaspete = mu + atac[oaspete] − apărare[gazdă].

    Estimare prin maximum likelihood cu pondere exp(−xi · vechime_în_zile) și
    penalizare L2 mică (echipele fără istoric rămân la media ligii = 0).
    rho (Dixon–Coles) se estimează într-un pas separat, după ratele Poisson (simplificare).
    """

    def __init__(self, xi: float = DEFAULT_XI, reg: float = 1.0, max_goals: int = 10,
                 use_rho: bool = True, max_age_days: int = 4 * 365):
        self.xi, self.reg, self.max_goals = xi, reg, max_goals
        self.use_rho, self.max_age_days = use_rho, max_age_days
        self.teams = {}
        self.att = self.dfn = np.zeros(0)
        self.mu = 0.0
        self.home_adv = 0.0
        self.rho = 0.0
        self.fitted = False

    def fit(self, matches, ref_date):
        """Antrenează pe meciuri; ref_date = „acum” (pentru vechime). Meciurile ≥ ref_date sunt ignorate."""
        rows = [m for m in matches if m["date"] < ref_date and (ref_date - m["date"]).days <= self.max_age_days]
        if not rows:
            self.fitted = False
            return self
        names = sorted({m["home"] for m in rows} | {m["away"] for m in rows})
        self.teams = {t: i for i, t in enumerate(names)}
        n = len(names)
        hi = np.array([self.teams[m["home"]] for m in rows])
        ai = np.array([self.teams[m["away"]] for m in rows])
        hg = np.array([m["hg"] for m in rows], float)
        ag = np.array([m["ag"] for m in rows], float)
        w = np.exp(-self.xi * np.array([(ref_date - m["date"]).days for m in rows], float))
        reg = self.reg

        def nll(theta):
            att, dfn, mu, h = theta[:n], theta[n:2 * n], theta[2 * n], theta[2 * n + 1]
            lh = np.exp(mu + h + att[hi] - dfn[ai])
            la = np.exp(mu + att[ai] - dfn[hi])
            val = np.sum(w * (lh - hg * np.log(lh) + la - ag * np.log(la)))
            val += reg * (np.sum(att ** 2) + np.sum(dfn ** 2))
            rh, ra = w * (lh - hg), w * (la - ag)
            g = np.zeros_like(theta)
            g[:n] = np.bincount(hi, rh, n) + np.bincount(ai, ra, n) + 2 * reg * att
            g[n:2 * n] = -np.bincount(ai, rh, n) - np.bincount(hi, ra, n) + 2 * reg * dfn
            g[2 * n] = rh.sum() + ra.sum()
            g[2 * n + 1] = rh.sum()
            return val, g

        x0 = np.zeros(2 * n + 2)
        avg_goals = np.average(np.concatenate([hg, ag]), weights=np.concatenate([w, w]))
        x0[2 * n] = math.log(max(avg_goals, 0.1))
        th = minimize(nll, x0, jac=True, method="L-BFGS-B").x
        self.att, self.dfn, self.mu, self.home_adv = th[:n], th[n:2 * n], th[2 * n], th[2 * n + 1]

        self.rho = 0.0
        if self.use_rho:
            lh = np.exp(self.mu + self.home_adv + self.att[hi] - self.dfn[ai])
            la = np.exp(self.mu + self.att[ai] - self.dfn[hi])
            s = (hg <= 1) & (ag <= 1)

            def neg(rho):
                t = np.ones(len(rows))
                t = np.where((hg == 0) & (ag == 0), 1 - lh * la * rho, t)
                t = np.where((hg == 0) & (ag == 1), 1 + lh * rho, t)
                t = np.where((hg == 1) & (ag == 0), 1 + la * rho, t)
                t = np.where((hg == 1) & (ag == 1), 1 - rho, t)
                return -np.sum(w[s] * np.log(np.maximum(t[s], 1e-9)))

            self.rho = float(minimize_scalar(neg, bounds=(-0.2, 0.2), method="bounded").x)
        self.fitted = True
        return self

    def rates(self, home: str, away: str):
        """(λ gazdă, λ oaspete); echipa necunoscută = media ligii."""
        i, j = self.teams.get(home), self.teams.get(away)
        ah = self.att[i] if i is not None else 0.0
        dh = self.dfn[i] if i is not None else 0.0
        aa = self.att[j] if j is not None else 0.0
        da = self.dfn[j] if j is not None else 0.0
        return (math.exp(self.mu + self.home_adv + ah - da), math.exp(self.mu + aa - dh))

    def score_matrix(self, home: str, away: str) -> np.ndarray:
        """P(gazdă = i, oaspete = j) pentru 0..max_goals goluri, normalizată."""
        lh, la = self.rates(home, away)
        k = np.arange(self.max_goals + 1)

        def pmf(lam):
            return np.exp(k * math.log(lam) - lam - gammaln(k + 1))

        mat = np.outer(pmf(lh), pmf(la))
        if self.rho:
            for x in (0, 1):
                for y in (0, 1):
                    mat[x, y] *= _tau(x, y, lh, la, self.rho)
        return mat / mat.sum()

    def predict(self, home: str, away: str) -> dict:
        """Probabilități 1X2 din matricea de scor (rânduri = goluri gazdă)."""
        mat = self.score_matrix(home, away)
        return {"home": float(np.tril(mat, -1).sum()), "draw": float(np.trace(mat)),
                "away": float(np.triu(mat, 1).sum())}
