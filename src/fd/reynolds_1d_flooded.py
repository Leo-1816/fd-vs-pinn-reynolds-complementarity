"""
1D Reynolds, flooded case with cavitation, with finite differences and the shooting method.

On [X_IN, X_OUT], with X_IN far upstream (stands for Xa = −∞):
    full film    X_IN ≤ X ≤ Xb : d/dX (H³ dP/dX) = dH/dX,  P(X_IN) = P(Xb) = 0
    cavitation   Xb < X ≤ X_OUT : P = 0
Xb is unknown: we look for it such that dP/dX(Xb) = 0 (Reynolds condition, also
called Swift-Stieber). For a given Xb, the pressure comes from fd.reynolds_1d.solve.

Expected references (flooded case, X_IN → −∞): W_ff ≈ 0.408, Xb = √(2(Hb_ff − 1)) ≈ 0.672.
"""

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import root_scalar

from fd import reynolds_1d

Positions = NDArray[np.float64]       # positions X, shape (n,)
PressureField = NDArray[np.float64]   # P(X), shape (n,)

X_IN = -10.0
X_OUT = 3.0
XB_BRACKET = (0.3, 1.0)   # dP/dX(Xb) < 0 at 0.3 (too early), > 0 at 1.0 (too late)


def outlet_slope(Xb: float, n: int) -> float:
    """dP/dX at Xb, for the pressure solved on [X_IN, Xb] with P = 0 at both ends.

    One-sided difference of order 2: (3 P[-1] − 4 P[-2] + P[-3]) / (2 ΔX).
    """

    solved = reynolds_1d.solve(X_IN, Xb, n)
    X : Positions = solved[0]
    P : PressureField = solved[1]
    dX = X[1] - X[0]
    slope_Xb = (3 * P[-1] - 4 * P[-2] + P[-3]) / (2 * dX)
    return slope_Xb


def find_cavitation_boundary(n: int) -> float:
    """Xb such that outlet_slope(Xb) = 0."""

    Xb = root_scalar(outlet_slope, args=(n,), bracket=XB_BRACKET, method="brentq").root
    return Xb


def solve(n: int) -> tuple[Positions, PressureField, float]:
    """P on n evenly spaced points of [X_IN, X_OUT], and Xb."""

    Xb = find_cavitation_boundary(n)
    solved = reynolds_1d.solve(X_IN, Xb, n)
    X_film : Positions = solved[0]
    P_film : PressureField = solved[1]

    # Full grid on [X_IN, X_OUT]
    X : Positions = np.linspace(X_IN, X_OUT, n)
    P : PressureField = np.zeros(n)

    # Interpolate the full-film pressure for X ≤ Xb
    P[X <= Xb] = np.interp(X[X <= Xb], X_film, P_film)

    return X, P, Xb
