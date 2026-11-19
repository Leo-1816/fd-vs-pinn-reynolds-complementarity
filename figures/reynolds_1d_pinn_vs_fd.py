"""Reynolds 1D sans cavitation : pression PINN vs FD, écarts sur W et F.

Lancer : uv run python figures/reynolds_1d_pinn_vs_fd.py
"""

import matplotlib.pyplot as plt
import torch

from analytical_solution.solution_1d import film_thickness
from fd import reynolds_1d as fd
from pinn import reynolds_1d as pinn
from pinn.plotting import plot_pinn_vs_fd_pressure
from pri.friction import friction_force, pressure_gradient, shear_stress_1D
from pri.load import load

# FD
X, P_fd = fd.solve(pinn.X_IN, pinn.X_OUT, 501)
dP_fd = pressure_gradient(X, P_fd)

# PINN
torch.manual_seed(pinn.SEED)
print(f"seed = {pinn.SEED}")
network = pinn.make_network()
pinn.train(network, pinn.make_sample_points(n_points=50))
P_pinn, dP_pinn = pinn.pressure_and_gradient(network, X)

# Charge et frottement (roulement pur, surface du bas)
H = film_thickness(X)
W_fd, W_pinn = load(X, P_fd), load(X, P_pinn)
F_fd = friction_force(X, shear_stress_1D(H, dP_fd, 0.0, 0.0, "bottom"))
F_pinn = friction_force(X, shear_stress_1D(H, dP_pinn, 0.0, 0.0, "bottom"))

plot_pinn_vs_fd_pressure(
    X, P_fd, P_pinn,
    title=f"Reynolds 1D sans cavitation, Hb = {pinn.HB} : PINN vs FD",
    subtitle=(f"Écart relatif : charge W {abs(W_pinn / W_fd - 1):.1e}, "
              f"frottement F (roulement pur) {abs(F_pinn / F_fd - 1):.1e}"),
)
plt.show()
