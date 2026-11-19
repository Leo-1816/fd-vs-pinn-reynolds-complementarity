"""Charge portée par le champ de pression (post-traitement commun FD et PINN).

Charge par unité de largeur, adimensionnée (rapport, éq. eq-adimensionnement) :

    W = ∫ P dX,      W = w h0 / (12 η0 um Rx)

Entrées en numpy : pour le PINN, convertir avec .detach().numpy().
"""

import numpy as np
from numpy.typing import NDArray

Positions = NDArray[np.float64]      # abscisses X, forme (n,)
PressureField = NDArray[np.float64]  # P(X), forme (n,)


def load(X: Positions, P: PressureField) -> float:
    """W = ∫ P dX sur la grille X.
    """
    return float(np.trapezoid(P, X))


# def half_sommerfeld_load(X: Positions, P: PressureField) -> float:
#     """W_HS = ∫ max(P, 0) dX : les pressions négatives sont mises à 0.
#     """
#     P_positive = np.maximum(P, 0)
#     return load(X, P_positive)


# def film_thickness_from_load(W: float, w: float, eta0: float, um: float,
#                              Rx: float) -> float:
#     """Chemin inverse : h0 [m] à partir de la charge imposée w [N/m] et de W.

#     On inverse W = w h0 / (12 η0 um Rx).
#     """
#     h0 = (12 * eta0 * um * Rx * W) / w
#     return h0
