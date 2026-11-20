"""Starved case with θ, FD (src/fd/reynolds_1d_starved.py) vs the analytical solution.

Reference: the 1D analytical solution (HDR §2.2.1) for the same amount of oil H_oil.
The FD unknown is u = P − θ: P is its positive part, θ its negative part.
"""

import numpy as np
import pytest

from analytical_solution import solution_1d as analytical
from fd import reynolds_1d_starved as starved
from pri.load import load

N_GRID = 641                      # 41 points refined 4 times
OIL_AMOUNTS = [1.02, 1.1, 1.2]    # little oil ... almost flooded (Xa from −0.29 to −2.9)


@pytest.fixture(scope="module", params=OIL_AMOUNTS)
def fd_and_exact(request):
    """FD and analytical solutions on the same grid, solved once per H_oil."""
    H_oil = request.param
    X, u, iterations = starved.solve(N_GRID, H_oil)
    P, theta = starved.pressure_and_void_fraction(u)
    exact = analytical.solve(H_oil, X)
    return X, P, theta, iterations, exact




def test_pressure_matches_analytical(fd_and_exact):
    _, P, _, _, exact = fd_and_exact
    assert np.max(np.abs(P - exact.P)) < 1e-3


def test_load_matches_analytical(fd_and_exact):
    X, P, _, _, exact = fd_and_exact
    assert load(X, P) == pytest.approx(exact.W, rel=5e-3)


def test_boundaries_match_analytical(fd_and_exact):
    """Xa = first pressurised point, Xb = last one. Tolerance: two grid cells."""
    X, P, _, _, exact = fd_and_exact
    pressurised = X[P > 0.0]
    two_cells = 2.0 * (X[1] - X[0])
    assert pressurised[0] == pytest.approx(exact.Xa, abs=two_cells)
    assert pressurised[-1] == pytest.approx(exact.Xb, abs=two_cells)


def test_void_fraction_matches_analytical_away_from_meniscus(fd_and_exact):
    """θ jumps at Xa: a meniscus one cell off gives a large but meaningless
    pointwise error there, so we leave out the points close to Xa."""
    X, _, theta, _, exact = fd_and_exact
    away_from_meniscus = np.abs(X - exact.Xa) > 0.05
    assert np.max(np.abs(theta - exact.theta)[away_from_meniscus]) < 5e-3


