"""
Solution analytique 1D du contact iso-visqueux-rigide sous-alimenté.

Source : HDR Biboulet 2020, §2.2.1 (détail dans
report/probleme_physique/solution_analytique.rst).

Idée : le débit d'huile Q = (1 − θ) H − H³ dP/dX vaut Hb partout. D'où trois zones :
    amont   X < Xa       : P = 0,  θ = 1 − Hb/H
    film    Xa ≤ X ≤ Xb  : θ = 0,  dP/dX = (H − Hb)/H³
    aval    X > Xb       : P = 0,  θ = 1 − Hb/H
Xb est explicite (H(Xb) = Hb) ; Xa est l'endroit, en amont, où P revient à 0.

Grandeurs adimensionnées ; θ = fraction de VIDE ; Y = X/√2 (variable de la HDR).
"""

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import root_scalar

Positions = NDArray[np.float64]       # abscisses X, forme (n,)
PressureField = NDArray[np.float64]   # P(X), forme (n,)
VoidFraction = NDArray[np.float64]    # θ(X), forme (n,)

X_FAR_UPSTREAM = -1e6   # « −∞ » pour chercher Xa (écart à la limite : O(1/X³))


@dataclass(frozen=True)
class AnalyticalSolution1D:
    """Solution pour une quantité d'huile Hb, évaluée sur la grille X."""

    X: Positions
    P: PressureField
    theta: VoidFraction
    Hb: float
    Xa: float
    Xb: float
    W: float


def film_thickness(X: Positions | float) -> Positions | float:
    """Épaisseur du film H(X) = 1 + X²/2."""
    return 1.0 + 0.5 * X**2


def pressure_primitive(Y: Positions | float, Hb: float) -> PressureField | float:
    """P_d(Y), primitive de dP/dX = (H − Hb)/H³ (HDR éq. 2.11), avec Y = X/√2."""
    H = 1.0 + Y**2
    return math.sqrt(2.0) * ((0.5 - 3.0 * Hb / 8.0) * (np.arctan(Y) + Y / H)
                             - Hb * Y / (4.0 * H**2))


def pressure_from_outlet(X: Positions | float, Hb: float) -> PressureField | float:
    """Pression intégrée depuis Xb (où P = 0), sans tenir compte de Xa."""
    Yb = math.sqrt(Hb - 1.0)
    return pressure_primitive(X / math.sqrt(2.0), Hb) - pressure_primitive(Yb, Hb)


def load_primitive(Y: float, Hb: float) -> float:
    """W_d(Y), primitive de la pression (HDR éq. 2.14), avec Y = X/√2."""
    Yb = math.sqrt(Hb - 1.0)
    H = 1.0 + Y**2
    return 2.0 * (Y * (0.5 - 3.0 * Hb / 8.0) * (math.atan(Y) - math.atan(Yb))
                  + Hb / (8.0 * H)
                  + Yb * Y * (3.0 / 8.0 - 1.0 / (4.0 * Hb)))


def solve(Hb: float, X: Positions) -> AnalyticalSolution1D:
    """Solution analytique pour 1 < Hb < Hb_ff ≈ 1,226 (sinon ValueError)."""
    if Hb <= 1.0:
        raise ValueError(f"Hb = {Hb} ≤ 1 : pas de zone sous pression")

    # 1. Sortie : P = 0 et dP/dX = 0, donc H(Xb) = Hb.
    Xb = math.sqrt(2.0 * (Hb - 1.0))

    # 2. Entrée : en remontant depuis Xb, P monte jusqu'en −Xb puis redescend ;
    #    Xa est l'endroit où elle revient à 0. Pas de racine si Hb ≥ Hb_ff.
    # On utilise la méthode de brent pour trouver Xa, avec un écart à la limite 
    # X_FAR_UPSTREAM.
    Xa = root_scalar(lambda x: float(pressure_from_outlet(x, Hb)),
                     bracket=(X_FAR_UPSTREAM, -Xb), xtol=1e-14, method='brentq').root

    # 3. Trois zones : film plein sur [Xa, Xb], P = 0 ailleurs.
    full_film = (X >= Xa) & (X <= Xb)
    P = np.where(full_film, pressure_from_outlet(X, Hb), 0.0)
    theta = np.where(full_film, 0.0, 1.0 - Hb / film_thickness(X))

    # 4. Charge : W = ∫ P dX sur [Xa, Xb].
    W = load_primitive(Xb / math.sqrt(2.0), Hb) - load_primitive(Xa / math.sqrt(2.0), Hb)

    return AnalyticalSolution1D(X=X, P=P, theta=theta, Hb=Hb, Xa=Xa, Xb=Xb, W=W)
