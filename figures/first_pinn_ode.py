"""Premier PINN, y' = -y, y(0) = 1 : réseau vs exp(-x) sur [0, X_MAX].

Lancer : uv run python figures/first_pinn_ode.py
"""

import matplotlib.pyplot as plt
import torch

from pinn.first_pinn_ode import SEED, X_MAX, exact_solution, make_network, make_sample_points, train
from pinn.plotting import plot_network_vs_exact_solution

torch.manual_seed(SEED)
print(f"seed = {SEED}")
network = make_network()
x_collocation = make_sample_points(n_points=50)
train(network, x_collocation)

with torch.no_grad():
    y_collocation = network(x_collocation)
plot_network_vs_exact_solution(
    network, exact_solution, x_collocation, y_collocation, 0.0, X_MAX,
    title="y' = -y, y(0) = 1 : PINN vs exp(-x)",
    network_label="PINN : y(x; w, b)",
    points_label=f"{len(x_collocation)} points de collocation",
)
plt.show()
