"""
Reynolds 1D, cas noyé avec cavitation, par différences finies et méthode de tir.

Sur [X_IN, X_OUT], avec X_IN loin en amont (approxime Xa = −∞) :
    film plein   X_IN ≤ X ≤ Xb : d/dX (H³ dP/dX) = dH/dX,  P(X_IN) = P(Xb) = 0
    cavitation   Xb < X ≤ X_OUT : P = 0
Xb est inconnu : on le cherche tel que dP/dX(Xb) = 0 (condition de Reynolds,
dite de Swift-Stieber). Pour un Xb donné, la pression vient de fd.reynolds_1d.solve.

Références attendues (cas noyé, X_IN → −∞) : W_ff ≈ 0,408, Xb = √(2(Hb_ff − 1)) ≈ 0,672.
"""

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import root_scalar

from fd import reynolds_1d

Positions = NDArray[np.float64]       # abscisses X, forme (n,)
PressureField = NDArray[np.float64]   # P(X), forme (n,)

X_IN = -10.0
X_OUT = 3.0
XB_BRACKET = (0.3, 1.0)   # dP/dX(Xb) < 0 en 0,3 (trop tôt), > 0 en 1,0 (trop tard)


def outlet_slope(Xb: float, n: int) -> float:
    """dP/dX en Xb, pour la pression résolue sur [X_IN, Xb] avec P = 0 aux deux bords.

    différence décentrée d'ordre 2, (3 P[-1] − 4 P[-2] + P[-3]) / (2 ΔX).
    """

    solved = reynolds_1d.solve(X_IN, Xb, n)
    X : Positions = solved[0]
    P : PressureField = solved[1]
    dX = X[1] - X[0]
    slope_Xb = (3 * P[-1] - 4 * P[-2] + P[-3]) / (2 * dX)
    return slope_Xb


def find_cavitation_boundary(n: int) -> float:
    """Xb tel que outlet_slope(Xb) = 0.
    """

    Xb = root_scalar(outlet_slope, args=(n,), bracket=XB_BRACKET, method="brentq").root
    return Xb


def solve(n: int) -> tuple[Positions, PressureField, float]:
    """P sur n points réguliers de [X_IN, X_OUT], et Xb.
    """

    Xb = find_cavitation_boundary(n)
    solved = reynolds_1d.solve(X_IN, Xb, n)
    X_film : Positions = solved[0]
    P_film : PressureField = solved[1]

    # Grille complète sur [X_IN, X_OUT]
    X : Positions = np.linspace(X_IN, X_OUT, n)
    P : PressureField = np.zeros(n)

    # Interpolation de la pression du film plein pour X ≤ Xb
    P[X <= Xb] = np.interp(X[X <= Xb], X_film, P_film)

    return X, P, Xb
