"""
1D analytical solution of the starved iso-viscous rigid contact.

Source: HDR Biboulet 2020, §2.2.1 (details in
report/probleme_physique/solution_analytique.rst).

Idea: the oil flow rate Q = (1 − θ) H − H³ dP/dX equals Hb everywhere. This gives three zones:
    upstream    X < Xa       : P = 0,  θ = 1 − Hb/H
    full film   Xa ≤ X ≤ Xb  : θ = 0,  dP/dX = (H − Hb)/H³
    downstream  X > Xb       : P = 0,  θ = 1 − Hb/H
Xb is explicit (H(Xb) = Hb). Xa is the place, upstream, where P comes back to 0.

Dimensionless quantities; θ = VOID fraction; Y = X/√2 (variable used in the HDR).
"""

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import root_scalar

Positions = NDArray[np.float64]       # positions X, shape (n,)
PressureField = NDArray[np.float64]   # P(X), shape (n,)
VoidFraction = NDArray[np.float64]    # θ(X), shape (n,)

X_FAR_UPSTREAM = -1e6   # "−∞" used to look for Xa (gap to the limit: O(1/X³))


@dataclass(frozen=True)
class AnalyticalSolution1D:
    """Solution for an amount of oil Hb, evaluated on the grid X."""

    X: Positions
    P: PressureField
    theta: VoidFraction
    Hb: float
    Xa: float
    Xb: float
    W: float


def film_thickness(X: Positions | float) -> Positions | float:
    """Film thickness H(X) = 1 + X²/2."""
    return 1.0 + 0.5 * X**2


def pressure_primitive(Y: Positions | float, Hb: float) -> PressureField | float:
    """P_d(Y), antiderivative of dP/dX = (H − Hb)/H³ (HDR eq. 2.11), with Y = X/√2."""
    H = 1.0 + Y**2
    return math.sqrt(2.0) * ((0.5 - 3.0 * Hb / 8.0) * (np.arctan(Y) + Y / H)
                             - Hb * Y / (4.0 * H**2))


def pressure_from_outlet(X: Positions | float, Hb: float) -> PressureField | float:
    """Pressure integrated from Xb (where P = 0), ignoring Xa."""
    Yb = math.sqrt(Hb - 1.0)
    return pressure_primitive(X / math.sqrt(2.0), Hb) - pressure_primitive(Yb, Hb)


def load_primitive(Y: float, Hb: float) -> float:
    """W_d(Y), antiderivative of the pressure (HDR eq. 2.14), with Y = X/√2."""
    Yb = math.sqrt(Hb - 1.0)
    H = 1.0 + Y**2
    return 2.0 * (Y * (0.5 - 3.0 * Hb / 8.0) * (math.atan(Y) - math.atan(Yb))
                  + Hb / (8.0 * H)
                  + Yb * Y * (3.0 / 8.0 - 1.0 / (4.0 * Hb)))


def solve(Hb: float, X: Positions) -> AnalyticalSolution1D:
    """Analytical solution for 1 < Hb < Hb_ff ≈ 1.226 (otherwise ValueError)."""
    if Hb <= 1.0:
        raise ValueError(f"Hb = {Hb} ≤ 1: no pressurised zone")

    # 1. Outlet: P = 0 and dP/dX = 0, so H(Xb) = Hb.
    Xb = math.sqrt(2.0 * (Hb - 1.0))

    # 2. Inlet: going upstream from Xb, P rises up to −Xb, then falls again;
    #    Xa is where it comes back to 0. No root if Hb ≥ Hb_ff.
    #    Brent's method finds Xa, with X_FAR_UPSTREAM standing for −∞.
    Xa = root_scalar(lambda x: float(pressure_from_outlet(x, Hb)),
                     bracket=(X_FAR_UPSTREAM, -Xb), xtol=1e-14, method='brentq').root

    # 3. Three zones: full film on [Xa, Xb], P = 0 elsewhere.
    full_film = (X >= Xa) & (X <= Xb)
    P = np.where(full_film, pressure_from_outlet(X, Hb), 0.0)
    theta = np.where(full_film, 0.0, 1.0 - Hb / film_thickness(X))

    # 4. Load: W = ∫ P dX over [Xa, Xb].
    W = load_primitive(Xb / math.sqrt(2.0), Hb) - load_primitive(Xa / math.sqrt(2.0), Hb)

    return AnalyticalSolution1D(X=X, P=P, theta=theta, Hb=Hb, Xa=Xa, Xb=Xb, W=W)
