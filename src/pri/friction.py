"""Frottement à partir de la pression (post-traitement commun FD et PINN).

Profil de vitesse de Reynolds intégré dans l'épaisseur, puis τ = η ∂u/∂z aux parois.
Forme adimensionnée (τ en unités de η um / h0) :

    τ = (U2 − U1) / H  ∓  6 H dP/dX   (− : surface du bas z = 0, + : surface du haut z = h)

    U1, U2 : vitesses des surfaces du bas et du haut, adimensionnées par um
    (U2 − U1 = 0 : roulement pur)

Signe : τ = η ∂u/∂z est la contrainte dans le fluide. La force exercée sur la
surface du bas vaut +τ(0), celle sur la surface du haut vaut −τ(h).

Frottement par unité de largeur, adimensionné (en unités de η um √(Rx/h0)) :

    F = ∫ τ dX

Film plein supposé (θ = 0) : pas encore de cavitation.
Entrées en numpy : pour le PINN, convertir avec .detach().numpy().
"""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

Positions = NDArray[np.float64]      # abscisses X, forme (n,)
ColumnValues = NDArray[np.float64]   # valeurs aux points X, forme (n,)
Surface = Literal["bottom", "top"]


def shear_stress_1D(H: ColumnValues, dP_dX: ColumnValues, U1: float,
                    U2: float, surface: Surface) -> ColumnValues:
    """τ(X) sur la surface choisie : Couette (U2 − U1)/H et Poiseuille ∓ 6 H dP/dX.

    Entrées : H(X), dP/dX(X), U1, U2 (vitesses aux surfaces z = 0 et z = h).
    """
    z = 0.0 if surface == "bottom" else H
    return 6.0 * (2.0 * z - H) * dP_dX + (U2 - U1) / H


def friction_force(X: Positions, tau: ColumnValues) -> float:
    """F = ∫ τ dX sur la grille X.

    """
    return float(np.trapezoid(tau, X))


def pressure_gradient(X: Positions, P: ColumnValues) -> ColumnValues:
    """dP/dX à partir des valeurs de P sur la grille (pour la FD).

    Pour le PINN, dP/dX vient directement d'autograd : cette fonction est inutile.

    """
    dP_dX = np.gradient(P, X)
    return dP_dX
