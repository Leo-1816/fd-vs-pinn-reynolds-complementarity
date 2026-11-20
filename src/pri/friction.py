"""Friction from the pressure (post-processing shared by FD and PINN).

Reynolds velocity profile across the thickness, then τ = η ∂u/∂z at the walls.
Dimensionless form (τ in units of η um / h0):

    τ = (U2 − U1) / H  ∓  6 H dP/dX   (−: bottom surface z = 0, +: top surface z = h)

    U1, U2: velocities of the bottom and top surfaces, divided by um
    (U2 − U1 = 0: pure rolling)

Sign: τ = η ∂u/∂z is the stress in the fluid. The force on the bottom surface
is +τ(0), the force on the top surface is −τ(h).

Friction per unit width, dimensionless (in units of η um √(Rx/h0)):

    F = ∫ τ dX

Full film assumed (θ = 0): no cavitation yet.
Inputs are numpy arrays: for the PINN, convert with .detach().numpy().
"""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

Positions = NDArray[np.float64]      # positions X, shape (n,)
ColumnValues = NDArray[np.float64]   # values at the points X, shape (n,)
Surface = Literal["bottom", "top"]


def shear_stress_1D(H: ColumnValues, dP_dX: ColumnValues, U1: float,
                    U2: float, surface: Surface) -> ColumnValues:
    """τ(X) on the chosen surface: Couette (U2 − U1)/H and Poiseuille ∓ 6 H dP/dX.

    Inputs: H(X), dP/dX(X), U1, U2 (velocities of the surfaces z = 0 and z = h).
    """
    z = 0.0 if surface == "bottom" else H
    return 6.0 * (2.0 * z - H) * dP_dX + (U2 - U1) / H


def friction_force(X: Positions, tau: ColumnValues) -> float:
    """F = ∫ τ dX on the grid X."""
    return float(np.trapezoid(tau, X))


def pressure_gradient(X: Positions, P: ColumnValues) -> ColumnValues:
    """dP/dX from the values of P on the grid (for FD).

    For the PINN, dP/dX comes directly from autograd: this function is not needed.
    """
    dP_dX = np.gradient(P, X)
    return dP_dX
