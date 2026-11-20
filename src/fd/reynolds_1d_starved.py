"""
1D Reynolds, starved case with the void fraction θ, with finite differences.

Method of the HDR (Biboulet 2020, §3.3.3, eqs. 3.51-3.61), written for 1D.

Equations at every point (report, eqs. eq-reynolds-theta and eq-fischer-burmeister):
    d/dX (H³ dP/dX) − d/dX ((1 − θ) H) = 0
    P ≥ 0,  θ ≥ 0,  P θ = 0

Boundary conditions:
    inlet   X_IN : P = 0 and θ = 1 − H_oil / H(X_IN)   (only the oil layer H_oil comes in)
    outlet  X_OUT: P = 0 just beyond the last point

The trick: a single unknown u = P − θ
    P = max(u, 0),   θ = max(−u, 0)
P and θ are never positive at the same time, so complementarity holds by
construction. Only the Reynolds equation is left: one equation per point.

Newton's method on u. At each iteration:
    r = A_P P + A_θ θ − dH          residual of Reynolds at every point
    J = A_P C_θ − A_θ C_P           Jacobian (HDR eq. 3.61)
    J δ = −r,   u ← u + δ
with C_θ = 1 where u > 0 (pressurised point) and C_P = 1 where u < 0 (cavitated point).

Discretisation (constant step ΔX):
    A_P : conservative Poiseuille term, H³ at the half points (HDR eq. 3.53-3.54)
          row i: H³_{i−1/2}/ΔX²,  −(H³_{i−1/2} + H³_{i+1/2})/ΔX²,  H³_{i+1/2}/ΔX²
    A_θ : derivative of θ H, upwind of order 2 (HDR eq. 3.55)
          row i: H_{i−2}/(2ΔX),  −4 H_{i−1}/(2ΔX),  3 H_i/(2ΔX)
    dH  : derivative of H with the same upwind formula
Why upwind: θ is carried by the flow from left to right, so its derivative uses
the points on the left (where the oil comes from).

Grid refinement (HDR §3.3.3): we solve on a coarse grid, interpolate the result
onto a grid twice as fine, solve again, and so on. The free boundaries then only
move a little on each level, which keeps Newton stable.

Checked in a quick prototype: H_oil = 1.1, final grid of 641 points → about
3 Newton iterations per level, error on P ≈ 4e-4, error on W ≈ 0.1 %.
The domain must contain the meniscus: X_IN < Xa (Xa ≈ −1.13 for H_oil = 1.1).
"""

import numpy as np
from numpy.typing import NDArray

from analytical_solution.solution_1d import film_thickness

Positions = NDArray[np.float64]       # positions X, shape (n,)
Unknown = NDArray[np.float64]         # u = P − θ, shape (n,)
Matrix = NDArray[np.float64]          # shape (n, n)

X_IN = -5.0
X_OUT = 2.0
RESIDUAL_TOLERANCE = 1e-10
MAX_NEWTON_ITERATIONS = 50


def build_matrices(X: Positions) -> tuple[Matrix, Matrix, NDArray[np.float64]]:
    """A_P, A_θ and dH for the grid X (they only depend on the geometry).
    """

    n = len(X)
    dX = X[1] - X[0]
    H = film_thickness(X)
    A_P = np.zeros((n, n))
    A_theta = np.zeros((n, n))
    dH = np.zeros(n)
    for i in range (1, n):
        # A_P
        if i < n - 1:
            H3_imh = film_thickness(0.5 * (X[i - 1] + X[i]))**3
            H3_iph = film_thickness(0.5 * (X[i] + X[i + 1]))**3
            A_P[i, i - 1] = H3_imh / dX**2
            A_P[i, i] = -(H3_imh + H3_iph) / dX**2
            A_P[i, i + 1] = H3_iph / dX**2
        else:
            H3_imh = film_thickness(0.5 * (X[i - 1] + X[i]))**3
            H3_iph = film_thickness(X[-1] + dX / 2)**3
            A_P[i, i - 1] = H3_imh / dX**2
            A_P[i, i] = -(H3_imh + H3_iph) / dX**2

        # A_theta and dH
        if i >= 2:
            A_theta[i, i - 2] = H[i - 2] / (2 * dX)
            A_theta[i, i - 1] = -4 * H[i - 1] / (2 * dX)
            A_theta[i, i] = 3 * H[i] / (2 * dX)
            dH[i] = (H[i - 2] - 4 * H[i - 1] + 3 * H[i]) / (2 * dX)
        else:
            A_theta[i, i - 1] = -H[i - 1] / dX
            A_theta[i, i] = H[i] / dX
            dH[i] = (H[i] - H[i - 1]) / dX
    return A_P, A_theta, dH


def pressure_and_void_fraction(u: Unknown) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """P = positive part of u, θ = negative part of u.
    """

    P = np.maximum(u, 0.0)
    theta = np.maximum(-u, 0.0)
    return P, theta


def newton_solve(X: Positions, u: Unknown, H_oil: float) -> tuple[Unknown, int]:
    """Newton's method on u, starting from the guess u. Returns u and the number of iterations.
    """

    A_P, A_theta, dH = build_matrices(X)
    u = u.copy()
    u[0] = -(1.0 - H_oil / film_thickness(X[0]))   # inlet: P = 0, θ = 1 − H_oil/H
    for iteration in range(MAX_NEWTON_ITERATIONS):
        P, theta = pressure_and_void_fraction(u)
        r = A_P @ P + A_theta @ theta - dH
        r[0] = 0.0
        if np.max(np.abs(r)) < RESIDUAL_TOLERANCE:
            return u, iteration
        C_theta = (u > 0.0).astype(float)
        C_P = 1.0 - C_theta
        J = A_P * C_theta[None, :] - A_theta * C_P[None, :]
        J[0, :] = 0.0
        J[0, 0] = 1.0
        u += np.linalg.solve(J, -r)
    return u, -1



def solve(n_final: int, H_oil: float, n_coarse: int = 41) -> tuple[Positions, Unknown, list[int]]:
    """Grid refinement from n_coarse points up to n_final points (n_final = 2^k (n_coarse − 1) + 1).

    Returns the final grid, u on it, and the number of Newton iterations per level.
    """

    X = np.linspace(X_IN, X_OUT, n_coarse)
    # First guess: no pressure, θ as if the oil were simply carried along.
    u: Unknown = -(1.0 - H_oil / np.asarray(film_thickness(X)))
    u, iterations = newton_solve(X, u, H_oil)
    iterations_per_level = [iterations]

    while len(X) < n_final:
        X_fine = np.linspace(X_IN, X_OUT, 2 * len(X) - 1)
        u = np.interp(X_fine, X, u)          # coarse result as the guess on the fine grid
        X = X_fine
        u, iterations = newton_solve(X, u, H_oil)
        iterations_per_level.append(iterations)

    return X, u, iterations_per_level
