"""Cas noyé avec cavitation par méthode de tir (src/fd/reynolds_1d_flooded.py).

Référence exacte à X_IN fini : P(X_IN) = 0 avec un film plein dès X_IN, c'est la
solution analytique (HDR §2.2.1) dont le ménisque est en Xa = X_IN. Son Hb
s'obtient par oil_quantity_from_meniscus (sens inverse du tableau HDR fig. 2.3).
"""

import numpy as np
import pytest

from analytical_solution import solution_1d as analytical
from fd import reynolds_1d_flooded as flooded
from pri.load import load
from test_analytical_solution import oil_quantity_from_meniscus

N_GRID = 2001


@pytest.fixture(scope="module")
def fd_and_exact():
    X, P, Xb = flooded.solve(N_GRID)
    exact = analytical.solve(oil_quantity_from_meniscus(flooded.X_IN), X)
    return X, P, Xb, exact


def test_cavitation_boundary_matches_analytical(fd_and_exact):
    _, _, Xb, exact = fd_and_exact
    assert Xb == pytest.approx(exact.Xb, abs=1e-4)


def test_load_matches_analytical(fd_and_exact):
    X, P, _, exact = fd_and_exact
    assert load(X, P) == pytest.approx(exact.W, rel=1e-4)


def test_pressure_matches_analytical(fd_and_exact):
    _, P, _, exact = fd_and_exact
    assert np.max(np.abs(P - exact.P)) < 1e-4


def test_pressure_is_zero_in_cavitation_zone(fd_and_exact):
    X, P, Xb, _ = fd_and_exact
    assert np.all(P[X > Xb] == 0.0)
