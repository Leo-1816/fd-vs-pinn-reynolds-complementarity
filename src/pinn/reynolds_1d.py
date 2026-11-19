"""PINN pour Reynolds 1D sans cavitation (rapport, éq. 2.7) :

    d/dX (H³ dP/dX) = dH/dX   sur [X_IN, X_OUT],   P(X_IN) = P(X_OUT) = 0,
    avec H(X) = 1 + X²/2.

Même démarche que first_pinn_ode.py, avec deux différences :
- l'équation est d'ordre 2 : il faut dériver deux fois par autograd ;
- deux conditions aux limites (une à chaque bord) au lieu d'une condition initiale.

Domaine : [Xa, Xb] de la solution analytique pour HB = 1,1 (frontières imposées,
comme pour la FD). La pression analytique sert UNIQUEMENT à vérifier.

Précision : float64, pour la même raison que first_pinn_ode.py.
"""

import numpy as np
import torch
from torch import nn

from analytical_solution import solution_1d as analytical

DTYPE = torch.float64
SEED = 0
BOUNDARY_PENALTY = 10.0  # facteur multiplicatif pour la perte aux bords

# ---------------------------------------------------------------------------
# 1. Le problème
# ---------------------------------------------------------------------------
HB = 1.1
_REFERENCE = analytical.solve(HB, np.array([0.0]))
X_IN = _REFERENCE.Xa
X_OUT = _REFERENCE.Xb

SamplePoints = torch.Tensor    # colonne de X, forme (n_points, 1)
ColumnValues = torch.Tensor    # valeurs associées, forme (n_points, 1)


def film_thickness(X: SamplePoints) -> ColumnValues:
    """H(X) = 1 + X²/2."""
    return 1.0 + 0.5 * X**2


def exact_pressure(X: SamplePoints) -> ColumnValues:
    """Pression analytique sur [Xa, Xb]. Pour la vérification uniquement."""
    P = analytical.pressure_from_outlet(X.detach().numpy(), HB)
    return torch.as_tensor(P, dtype=DTYPE)


def make_sample_points(n_points: int) -> SamplePoints:
    """Points réguliers sur [X_IN, X_OUT], forme (n_points, 1), avec requires_grad."""
    X = torch.linspace(X_IN, X_OUT, n_points, dtype=DTYPE).reshape(-1, 1)
    return X.requires_grad_(True)


# ---------------------------------------------------------------------------
# 2. Le réseau
# ---------------------------------------------------------------------------
def make_network(hidden_width: int = 20) -> nn.Module:
    """X -> P, deux couches cachées tanh (dérivée seconde non nulle, contrairement à ReLU)."""
    return nn.Sequential(
        nn.Linear(1, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, 1),
    ).to(DTYPE)


# ---------------------------------------------------------------------------
# 3. Le résidu de Reynolds
# ---------------------------------------------------------------------------
def reynolds_residual(network: nn.Module, X: SamplePoints) -> ColumnValues:
    """Renvoie r(X) = d/dX (H³ dP/dX) − dH/dX, forme (n_points, 1).

    Indice : calculer P, puis dP/dX par autograd, puis le flux H³ dP/dX,
    puis sa dérivée par autograd. dH/dX peut aussi s'obtenir par autograd.
    """
    P = network(X)
    dP_dX = torch.autograd.grad(P, X, grad_outputs=torch.ones_like(P), create_graph=True)[0]
    H = film_thickness(X)
    flux = H**3 * dP_dX
    d_flux_dX = torch.autograd.grad(flux, X, grad_outputs=torch.ones_like(flux), create_graph=True)[0]
    dH_dX = torch.autograd.grad(H, X, grad_outputs=torch.ones_like(H), create_graph=True)[0]
    residual = d_flux_dX - dH_dX
    return residual


# ---------------------------------------------------------------------------
# 4. La perte
# ---------------------------------------------------------------------------
def pinn_loss(network: nn.Module, X: SamplePoints) -> torch.Tensor:
    """Renvoie un SCALAIRE : moyenne(r²) + poids * (P(X_IN)² + P(X_OUT)²)."""
    residual = reynolds_residual(network, X)
    P_in = network(torch.tensor([[X_IN]], dtype=DTYPE))
    P_out = network(torch.tensor([[X_OUT]], dtype=DTYPE))
    loss = torch.mean(residual**2) + BOUNDARY_PENALTY*P_in**2 + BOUNDARY_PENALTY*P_out**2
    return loss


# ---------------------------------------------------------------------------
# 5. La boucle d'entraînement
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    X: SamplePoints,
    n_epochs: int = 5000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimise pinn_loss avec Adam. Renvoie l'historique de la perte."""
    optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    loss_history = []
    for epoch in range(n_epochs):
        optimizer.zero_grad()
        loss = pinn_loss(network, X)
        loss.backward()
        optimizer.step()
        loss_history.append(loss.item())
        if epoch % 500 == 0:
            print(f"Epoch {epoch:5d}, Loss = {loss.item():.3e}")
    return loss_history


# ---------------------------------------------------------------------------
# 6. La vérification
# ---------------------------------------------------------------------------
def max_error_against_exact_pressure(network: nn.Module, n_test_points: int = 201) -> float:
    """Erreur max |P(X; w, b) − P_analytique| sur des points de test."""
    X_test = torch.linspace(X_IN, X_OUT, n_test_points, dtype=DTYPE).reshape(-1, 1)
    with torch.no_grad():
        prediction = network(X_test)
    return (prediction - exact_pressure(X_test)).abs().max().item()


def pressure_and_gradient(network: nn.Module, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """P et dP/dX (autograd) du réseau sur la grille X, en numpy (pour friction et load)."""
    X_column = torch.as_tensor(X, dtype=DTYPE).reshape(-1, 1).requires_grad_(True)
    P = network(X_column)
    dP_dX = torch.autograd.grad(P.sum(), X_column)[0]
    return P.detach().numpy().ravel(), dP_dX.numpy().ravel()


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}, Hb = {HB}, domaine = [{X_IN:.4f}, {X_OUT:.4f}]")

    network = make_network()
    X_collocation = make_sample_points(n_points=50)

    print(f"Erreur max AVANT entraînement : {max_error_against_exact_pressure(network):.3e}")
    train(network, X_collocation)
    print(f"Erreur max APRÈS entraînement : {max_error_against_exact_pressure(network):.3e}")


if __name__ == "__main__":
    main()
