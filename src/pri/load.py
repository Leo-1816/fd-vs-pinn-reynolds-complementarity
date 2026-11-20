"""Load carried by the pressure field (post-processing shared by FD and PINN).

Load per unit width, dimensionless (report, eq. eq-adimensionnement):

    W = ∫ P dX,      W = w h0 / (12 η0 um Rx)

Inputs are numpy arrays: for the PINN, convert with .detach().numpy().
"""

import numpy as np
from numpy.typing import NDArray

Positions = NDArray[np.float64]      # positions X, shape (n,)
PressureField = NDArray[np.float64]  # P(X), shape (n,)


def load(X: Positions, P: PressureField) -> float:
    """W = ∫ P dX on the grid X."""
    return float(np.trapezoid(P, X))


# def half_sommerfeld_load(X: Positions, P: PressureField) -> float:
#     """W_HS = ∫ max(P, 0) dX: negative pressures are set to 0.
#     """
#     P_positive = np.maximum(P, 0)
#     return load(X, P_positive)


# def film_thickness_from_load(W: float, w: float, eta0: float, um: float,
#                              Rx: float) -> float:
#     """Inverse path: h0 [m] from the imposed load w [N/m] and from W.

#     We invert W = w h0 / (12 η0 um Rx).
#     """
#     h0 = (12 * eta0 * um * Rx * W) / w
#     return h0
