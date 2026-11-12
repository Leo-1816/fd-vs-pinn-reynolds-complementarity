"""Ajustement supervisé de sin(x) par un MLP : données d'entraînement et
interpolation par le réseau sur [X_MIN, X_MAX].

Lancer : uv run python figures/fit_sine_mlp.py
"""

import matplotlib.pyplot as plt
import torch

from pinn.fit_sine_mlp import SEED, X_MAX, X_MIN, make_network, make_training_data, target_function, train
from pinn.plotting import plot_network_vs_exact_solution

torch.manual_seed(SEED)
print(f"seed = {SEED}")
network = make_network()
x_train, y_train = make_training_data(n_points=8)
train(network, x_train, y_train)

plot_network_vs_exact_solution(
    network, target_function, x_train, y_train, X_MIN, X_MAX,
    title="Ajustement de sin(x) par un MLP",
    network_label="MLP : y(x; w, b)",
    points_label=f"{len(x_train)} données d'entraînement sin(x_i)",
)
plt.show()
