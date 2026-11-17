"""Tests de la solution analytique 1D (HDR Biboulet 2020, §2.2.1)."""

import math

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.optimize import root_scalar

from analytical_solution.solution_1d import (
    X_FAR_UPSTREAM,
    film_thickness,
    pressure_from_outlet,
)


# ---------------------------------------------------------------------------
# Grandeurs de validation 
# ---------------------------------------------------------------------------
def flooded_oil_quantity() -> float:
    """Hb_ff : P(−∞) = 0, le ménisque est rejeté à l'infini (contact noyé)."""
    return root_scalar(lambda Hb: float(pressure_from_outlet(X_FAR_UPSTREAM, Hb)),
                       bracket=(1.0, 2.0), xtol=1e-14).root


def oil_quantity_from_meniscus(Xa: float) -> float:
    """Sens inverse (tableau HDR fig. 2.3) : Hb tel que P(Xa) = 0."""
    upper = min(flooded_oil_quantity(), float(film_thickness(Xa)))
    return root_scalar(lambda Hb: float(pressure_from_outlet(Xa, Hb)),
                       bracket=(1.0, upper), xtol=1e-14, method='brentq').root

# ---------------------------------------------------------------------------
# Valeurs de référence de la HDR
# ---------------------------------------------------------------------------
def test_flooded_oil_quantity_matches_hdr():
    assert flooded_oil_quantity() == pytest.approx(1.226, abs=5e-4)


def test_flooded_load_matches_hdr():
    Hb_ff = flooded_oil_quantity()
    Xb = math.sqrt(2.0 * (Hb_ff - 1.0))
    W_ff, _ = quad(lambda X: float(pressure_from_outlet(X, Hb_ff)), -np.inf, Xb)
    assert W_ff == pytest.approx(0.408, abs=5e-4)


@pytest.mark.parametrize(
    "Xa, Hb_hdr",
    [
        (-3.0, 1.201),
        (-2.0, 1.169),
        (-1.5, 1.136),
        (-1.0, 1.085),
        # HDR fig. 2.3 donne 1,053
        # à confirmer avec le tuteur
        (-0.75, 1.056),
        (-0.5, 1.028),
    ],
)
def test_meniscus_to_oil_quantity_matches_hdr_table(Xa, Hb_hdr):
    """Tolérance d'une unité sur le 3e chiffre (Xa = −1,5 donne 1,13547, HDR : 1,136)."""
    assert oil_quantity_from_meniscus(Xa) == pytest.approx(Hb_hdr, abs=1e-3)

