"""Tests du solveur FD de Reynolds 1D sans cavitation (src/fd/reynolds_1d.py).

Référence : sur [Xa, Xb] donnés par la solution analytique (HDR §2.2.1),
P = 0 aux deux bords, donc le FD doit retrouver la pression analytique.
"""

import numpy as np
import pytest

from analytical_solution import solution_1d as analytical
from fd import reynolds_1d as fd

HB = 1.1


def max_error(n: int) -> float:
    ref = analytical.solve(HB, np.array([0.0]))
    X, P = fd.solve(ref.Xa, ref.Xb, n) # On considère que le solveur FD 
    # est appliqué sur l'intervalle [Xa, Xb] de la solution analytique.
    P_exact = analytical.pressure_from_outlet(X, HB)
    return float(np.max(np.abs(P - P_exact)))


def test_matches_analytical_pressure():
    assert max_error(2001) < 1e-6


def test_second_order_convergence():
    order = np.log2(max_error(201) / max_error(401))
    assert order == pytest.approx(2.0, abs=0.1)
