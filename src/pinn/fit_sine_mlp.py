"""

Apprentissage supervisé : on fournit au réseau des points d'entraînement 
(x_i, sin(x_i)) et on minimise la perte MSE = moyenne((y(x_i; w, b) - sin(x_i))^2).

La fonction à apprendre est définie dans target_function(x). 
Pour apprendre une autre fonction, il suffit de modifier cette fonction.


"""

import math

import torch
from torch import nn

DTYPE = torch.float64
SEED = 0

# ---------------------------------------------------------------------------
# 1. Les données
# ---------------------------------------------------------------------------
X_MIN = -math.pi
X_MAX = math.pi

SamplePoints = torch.Tensor   # forme (n_points, 1)
ColumnValues = torch.Tensor   # forme (n_points, 1)


# ---------------------------------------------------------
# ---------------------------------------------------------
# Fonction à apprendre 
# Seul détail à changer pour apprendre une autre fonction


def target_function(x: SamplePoints) -> ColumnValues:
    """La fonction à apprendre : sin(x)."""
    return torch.sin(x)

# ---------------------------------------------------------
# ---------------------------------------------------------


def make_training_data(n_points: int) -> tuple[SamplePoints, ColumnValues]:
    """Points régulièrement espacés sur [X_MIN, X_MAX] et valeurs sin(x) associées.
    Pas de requires_grad : on ne dérive pas par rapport à x."""
    x = torch.linspace(X_MIN, X_MAX, n_points, dtype=DTYPE).reshape(-1, 1)
    return x, target_function(x)


# ---------------------------------------------------------------------------
# 2. Le réseau
# ---------------------------------------------------------------------------
def make_network(hidden_width: int = 20) -> nn.Module:
    """x (1 valeur) -> y (1 valeur), une couche cachée tanh de hidden_width neurones."""
    return nn.Sequential(
        nn.Linear(1, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, 1)).to(DTYPE)


# ---------------------------------------------------------------------------
# 3. La perte
# ---------------------------------------------------------------------------
def mean_squared_error_loss(
    network: nn.Module, x: SamplePoints, y_target: ColumnValues
) -> torch.Tensor:
    """Renvoie un SCALAIRE : moyenne de (y(x; w, b) - sin(x))^2.
    """

    y_pred = network(x)
    loss = torch.mean((y_pred - y_target) ** 2)
    return loss


# ---------------------------------------------------------------------------
# 4. La boucle d'entraînement
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    x: SamplePoints,
    y_target: ColumnValues,
    n_epochs: int = 5000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimise mean_squared_error_loss avec Adam. Renvoie l'historique de la perte.

    Mêmes 4 étapes par itération que pour le PINN : seule la perte change.
    """
    optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    loss_history: list[float] = []

    for epoch in range(n_epochs):
        optimizer.zero_grad()
        loss = mean_squared_error_loss(network, x, y_target)
        loss.backward()
        optimizer.step()

        loss_history.append(loss.item())
        if epoch % 500 == 0:
            print(f"  epoch {epoch:5d}   perte = {loss.item():.3e}")

    return loss_history


# ---------------------------------------------------------------------------
# 5. La vérification
# ---------------------------------------------------------------------------
def max_error_against_target(network: nn.Module, n_test_points: int = 401) -> float:
    """Erreur max |y(x; w, b) - sin(x)| sur des points de TEST, plus nombreux
    que les points d'entraînement : le réseau a-t-il appris la fonction
    entre les points, ou seulement par coeur aux points d'entraînement ?"""
    x_test = torch.linspace(X_MIN, X_MAX, n_test_points, dtype=DTYPE).reshape(-1, 1)
    with torch.no_grad():
        prediction = network(x_test)
    return (prediction - target_function(x_test)).abs().max().item()


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}")

    network = make_network()
    x_train, y_train = make_training_data(n_points=50)

    print(f"Erreur max AVANT entraînement : {max_error_against_target(network):.3e}")
    train(network, x_train, y_train)
    print(f"Erreur max APRÈS entraînement : {max_error_against_target(network):.3e}")




if __name__ == "__main__":
    main()
