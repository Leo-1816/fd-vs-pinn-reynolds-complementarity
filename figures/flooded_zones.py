"""Cas noyé : schéma des zones (film plein / cavitation) et du résidu r, solution FD.

Lancer : uv run python figures/flooded_zones.py
"""

import matplotlib.pyplot as plt

from fd.plotting import plot_flooded_zones
from fd.reynolds_1d_flooded import X_OUT, solve

X, P, Xb = solve(n=2001)
plot_flooded_zones(X, P, Xb, x_min=-4.0, x_max=X_OUT)
plt.show()
