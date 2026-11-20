"""1D Reynolds without cavitation: load W and friction F, FD and PINN vs analytical.

On [Xa, Xb] (Hb = 1.1), the analytical solution (HDR §2.2.1) exactly satisfies
the problem without cavitation: it is the reference for both methods.
"""

import numpy as np
import pytest
import torch

from analytical_solution import solution_1d as analytical
from fd import reynolds_1d as fd
from pinn import reynolds_1d as pinn
from pri.friction import Surface, friction_force, pressure_gradient, shear_stress_1D
from pri.load import load

N_GRID = 501
RELATIVE_TOLERANCE = 1e-3

X = np.linspace(pinn.X_IN, pinn.X_OUT, N_GRID)
H = analytical.film_thickness(X)


def friction(dP_dX: np.ndarray, U2: float, surface: Surface) -> float:
    return friction_force(X, shear_stress_1D(H, dP_dX, 0.0, U2, surface))


@pytest.fixture(scope="module")
def solutions() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """P and dP/dX on the grid X, for each method."""
    # Analytical: P from the HDR, dP/dX = (H − Hb)/H³ (constant flow rate)
    P_exact = analytical.pressure_from_outlet(X, pinn.HB)
    dP_exact = (H - pinn.HB) / H**3

    # FD
    _, P_fd = fd.solve(pinn.X_IN, pinn.X_OUT, N_GRID)
    dP_fd = pressure_gradient(X, P_fd)

    # PINN (fixed seed), trained only once for the whole file
    torch.manual_seed(pinn.SEED)
    network = pinn.make_network()
    pinn.train(network, pinn.make_sample_points(n_points=50))
    P_pinn, dP_pinn = pinn.pressure_and_gradient(network, X)

    return {"analytical": (P_exact, dP_exact), "FD": (P_fd, dP_fd), "PINN": (P_pinn, dP_pinn)}


def test_analytical_load_matches_hdr_formula(solutions):
    """Check of the reference: numerical ∫ P dX = analytical W (HDR eq. 2.14)."""
    P_exact, _ = solutions["analytical"]
    W_hdr = analytical.solve(pinn.HB, X).W
    assert load(X, P_exact) == pytest.approx(W_hdr, rel=RELATIVE_TOLERANCE)


@pytest.mark.parametrize("method", ["FD", "PINN"])
def test_load_matches_analytical(solutions, method: str):
    W_exact = analytical.solve(pinn.HB, X).W
    P, _ = solutions[method]
    assert load(X, P) == pytest.approx(W_exact, rel=RELATIVE_TOLERANCE)


@pytest.mark.parametrize("method", ["FD", "PINN"])
@pytest.mark.parametrize("surface", ["bottom", "top"])
@pytest.mark.parametrize("U2", [0.0, 1.0])   # pure rolling, then sliding
def test_friction_matches_analytical(solutions, method: str, U2: float, surface: Surface):
    _, dP_exact = solutions["analytical"]
    _, dP = solutions[method]
    assert friction(dP, U2, surface) == pytest.approx(friction(dP_exact, U2, surface),
                                                      rel=RELATIVE_TOLERANCE)
