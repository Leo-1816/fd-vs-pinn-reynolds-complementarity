"""
Équation de Reynolds 1D sans cavitation, par différences finies.

Équation résolue (rapport, éq. 2.7) :
    d/dX (H³ dP/dX) = dH/dX   sur [X_in, X_out],   P(X_in) = P(X_out) = 0.
"""

import numpy as np
from numpy.typing import NDArray

from analytical_solution.solution_1d import film_thickness

Positions = NDArray[np.float64]       # abscisses X, forme (n,)
PressureField = NDArray[np.float64]   # P(X), forme (n,)


def solve(X_in: float, X_out: float, n: int) -> tuple[Positions, PressureField]:
    """P sur n points réguliers de [X_in, X_out], avec P = 0 aux deux bords."""
    # 1. Grille
    X : Positions = np.linspace(X_in, X_out, n)
    dX = X[1] - X[0]

    # 2. H et dH/dX aux points de la grille
    H = film_thickness(X)
    dH = X    # H = 1 + X²/2 ⇒ dH/dX = X

    # 3. Système A P = b
    A = np.zeros((n, n))
    b = np.zeros(n)

    # Bords : P = 0
    A[0, 0] = 1.0
    A[-1, -1] = 1.0   # P(X_out) = 0


    # Points intérieurs : H³ P'' + 3 H² H' P' = H'
    # P'' ≈ (Pᵢ₋₁ − 2Pᵢ + Pᵢ₊₁) / ΔX²
    #P' ≈ (Pᵢ₊₁ − Pᵢ₋₁) / (2ΔX)

    for i in range(1, n - 1):
        H_i = H[i]
        H3 = H_i**3
        dH_i = dH[i]

        A[i, i - 1] = H3 / dX**2 - (3 * H_i**2 * dH_i) / (2 * dX)
        A[i, i] = -2 * H3 / dX**2
        A[i, i + 1] = H3 / dX**2 + (3 * H_i**2 * dH_i) / (2 * dX)

        b[i] = dH_i

    # 4. Résolution
    P = np.linalg.solve(A, b)
    return X, P
