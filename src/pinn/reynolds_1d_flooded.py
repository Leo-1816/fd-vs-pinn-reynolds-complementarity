"""PINN pour Reynolds 1D, cas noyé avec cavitation (même problème que fd/reynolds_1d_flooded.py).

Sur [X_IN, X_OUT], P(X_IN) = P(X_OUT) = 0. On ne connaît pas Xb : on impose la
complémentarité entre la pression et le résidu de Reynolds r (sans θ) :

    P ≥ 0,   −r ≥ 0,   P · r = 0

    - film plein (P > 0)  : r = 0, Reynolds est vérifiée ;
    - zone cavitée (P = 0) : r ≤ 0 suffit (pénaliser seulement P < 0 ne marche
      pas : en zone cavitée, r = −dH/dX ≠ 0, le réseau devrait choisir entre les deux).

Les trois conditions tiennent en une seule équation (Fischer-Burmeister, comme
dans le rapport, éq. eq-fischer-burmeister, avec θ remplacé par −r) :

    φ(P, −r) = P − r − √(P² + r²) = 0
"""

import numpy as np
import torch
from scipy.optimize import root_scalar
from torch import nn

from analytical_solution import solution_1d as analytical
from pinn.reynolds_1d import film_thickness, reynolds_residual

DTYPE = torch.float64
SEED = 0
BOUNDARY_PENALTY = 10.0
SQRT_EPSILON = 1e-20

# ---------------------------------------------------------------------------
# 1. Le problème
# ---------------------------------------------------------------------------
X_IN = -10.0
X_OUT = 3.0

SamplePoints = torch.Tensor    # colonne de X, forme (n_points, 1)
ColumnValues = torch.Tensor    # valeurs associées, forme (n_points, 1)


def make_sample_points(n_points: int) -> SamplePoints:
    """Points réguliers sur [X_IN, X_OUT], forme (n_points, 1), avec requires_grad."""
    X = torch.linspace(X_IN, X_OUT, n_points, dtype=DTYPE).reshape(-1, 1)
    return X.requires_grad_(True)


# ---------------------------------------------------------------------------
# 2. Le réseau
# ---------------------------------------------------------------------------
class PressureNetwork(nn.Module):
    """X -> P. X est d'abord ramené dans [−1, 1], puis trois couches cachées tanh."""

    def __init__(self, hidden_width: int = 30) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1, hidden_width), nn.Tanh(),
            nn.Linear(hidden_width, hidden_width), nn.Tanh(),
            nn.Linear(hidden_width, hidden_width), nn.Tanh(),
            nn.Linear(hidden_width, 1),
        ).to(DTYPE)

    def forward(self, X: SamplePoints) -> ColumnValues:
        X_normalized = (2.0 * X - (X_IN + X_OUT)) / (X_OUT - X_IN)
        return self.layers(X_normalized)


# ---------------------------------------------------------------------------
# 3. Le résidu de complémentarité
# ---------------------------------------------------------------------------
def complementarity_residual(network: nn.Module, X: SamplePoints) -> ColumnValues:
    """Renvoie φ(P, −r/H³) = P − r/H³ − √(P² + (r/H³)²), forme (n_points, 1).

    Indice : r vient de reynolds_residual (déjà écrit dans pinn/reynolds_1d.py),
    H de film_thickness.
    """
    r = reynolds_residual(network, X)
    H = film_thickness(X)
    P = network(X)
    r_scaled = r / H**3
    # SQRT_EPSILON : évite une dérivée infinie de √ quand P = r = 0
    return P - r_scaled - torch.sqrt(P**2 + r_scaled**2 + SQRT_EPSILON)


# ---------------------------------------------------------------------------
# 4. La perte
# ---------------------------------------------------------------------------
def pinn_loss(network: nn.Module, X: SamplePoints) -> torch.Tensor:
    """Renvoie un SCALAIRE : moyenne(φ²) + BOUNDARY_PENALTY (P(X_IN)² + P(X_OUT)²)."""
    phi = complementarity_residual(network, X)
    P_in = network(torch.tensor([[X_IN]], dtype=DTYPE))
    P_out = network(torch.tensor([[X_OUT]], dtype=DTYPE))
    loss = torch.mean(phi**2) + BOUNDARY_PENALTY * (P_in**2 + P_out**2).squeeze()
    return loss


# ---------------------------------------------------------------------------
# 5. La boucle d'entraînement
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    X: SamplePoints,
    n_epochs: int = 15000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimise pinn_loss avec Adam (même boucle que pinn/reynolds_1d.py)."""
    optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    loss_history: list[float] = []
    for epoch in range(1, n_epochs + 1):
        optimizer.zero_grad()
        loss = pinn_loss(network, X)
        loss.backward()
        optimizer.step()
        loss_history.append(loss.item())
        if epoch % 1000 == 0:
            print(f"Epoch {epoch:5d}, loss = {loss.item():.3e}")
    return loss_history


# ---------------------------------------------------------------------------
# 6. La vérification
# ---------------------------------------------------------------------------
def exact_solution(X: np.ndarray) -> analytical.AnalyticalSolution1D:
    """Solution analytique dont le ménisque est en Xa = X_IN (cf. test FD cas noyé)."""
    Hb = root_scalar(lambda h: float(analytical.pressure_from_outlet(X_IN, h)),
                     bracket=(1.0, 1.2258), method="brentq").root
    return analytical.solve(Hb, X)


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}, domaine = [{X_IN}, {X_OUT}]")

    network = PressureNetwork()
    train(network, make_sample_points(n_points=400))

    X_test = np.linspace(X_IN, X_OUT, 2001)
    exact = exact_solution(X_test)
    with torch.no_grad():
        P = network(torch.as_tensor(X_test, dtype=DTYPE).reshape(-1, 1)).numpy().ravel()
    print(f"Erreur max sur P : {np.max(np.abs(P - exact.P)):.3e}  (P max = {exact.P.max():.3f})")
    print(f"W PINN = {np.trapezoid(P, X_test):.4f}, W exacte = {exact.W:.4f}")


if __name__ == "__main__":
    main()
