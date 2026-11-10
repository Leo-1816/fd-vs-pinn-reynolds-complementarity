"""Premier PINN : résoudre y'(x) = -y(x) sur [0, X_MAX], avec y(0) = 1.

Solution exacte : y(x) = exp(-x)  (sert UNIQUEMENT à vérifier, jamais dans la perte).

------------------------------------------------------------------------------
L'idée en une phrase
------------------------------------------------------------------------------
On ne cherche pas y(x) comme une liste de valeurs (comme en FD), on cherche
un réseau de neurones y(x; w, b) dont les poids w et les biais b sont tels
que l'équation soit vérifiée. On transforme donc "résoudre l'EDO" en
"minimiser une perte" :

    perte(w, b) =  moyenne sur les x_i de [ y'(x_i; w, b) + y(x_i; w, b) ]^2   <- résidu de l'EDO
                 + [ y(0; w, b) - 1 ]^2                                        <- condition initiale

Si la perte vaut 0, alors y' + y = 0 en tous les x_i ET y(0) = 1 :
y(x; w, b) est (approximativement) la solution. On n'a jamais donné exp(-x)
au réseau, seulement l'équation.

Les x_i sont les "points de collocation" : les endroits où on vérifie
l'équation. Ils jouent un peu le rôle des noeuds en FD.

------------------------------------------------------------------------------
Ce qu'on réutilise du fichier autograd_derivatives.py
------------------------------------------------------------------------------
- x.requires_grad_(True) sur les points de collocation, pour pouvoir dériver
  la sortie du réseau par rapport à x.
- torch.autograd.grad(..., create_graph=True) pour obtenir y'(x).
  create_graph=True est indispensable ici : la perte contient y', et on doit
  ensuite dériver la perte par rapport aux poids w et biais b (backward).
  Sans graphe, pas de gradient pour w et b.

------------------------------------------------------------------------------
Plan du fichier (à compléter ensemble, cherche les "TODO")
------------------------------------------------------------------------------
1. Le problème (donné)
2. Le réseau (donné)
3. Le résidu de l'EDO          <- TODO 1
4. La perte                    <- TODO 2
5. La boucle d'entraînement    <- TODO 3
6. La vérification (donnée)

Précision : float64. Le problème est minuscule, donc le coût est négligeable,
et on évite que l'erreur d'arrondi float32 (~1e-7) se mélange à l'erreur
du PINN quand on la mesurera.


"""

import torch
from torch import nn

DTYPE = torch.float64
SEED = 0

# ---------------------------------------------------------------------------
# 1. Le problème
# ---------------------------------------------------------------------------
X_MAX = 2.0
INITIAL_POINT = 0.0
INITIAL_VALUE = 1.0

# Types : une colonne de points, forme (n_points, 1), et les valeurs associées.
SamplePoints = torch.Tensor
ColumnValues = torch.Tensor


def exact_solution(x: SamplePoints) -> ColumnValues:
    """y(x) = exp(-x). Pour la vérification uniquement."""
    return torch.exp(-x)


def make_sample_points(n_points: int) -> SamplePoints:
    """Points régulièrement espacés sur [0, X_MAX], forme (n_points, 1),
    avec requires_grad pour pouvoir calculer y'(x) par autograd."""
    x = torch.linspace(0.0, X_MAX, n_points, dtype=DTYPE).reshape(-1, 1)
    return x.requires_grad_(True)


# ---------------------------------------------------------------------------
# 2. Le réseau
# ---------------------------------------------------------------------------
def make_network(hidden_width: int = 20) -> nn.Module:
    """x (1 valeur) -> y (1 valeur), deux couches cachées tanh.

    tanh plutôt que ReLU : ReLU est linéaire par morceaux, sa dérivée seconde
    est nulle presque partout. Ici on n'a besoin que de y', mais on prend
    l'habitude dès maintenant (pour y'' + y = 0 en semaine 2, ReLU échouerait).
    """
    return nn.Sequential(
        nn.Linear(1, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, 1),
    ).to(DTYPE)


# ---------------------------------------------------------------------------
# 3. Le résidu de l'EDO          
# ---------------------------------------------------------------------------
def ode_residual(network: nn.Module, x: SamplePoints) -> ColumnValues:
    """Renvoie r(x) = y'(x) + y(x), forme (n_points, 1).

    """
    y = network(x)
    y_prime = torch.autograd.grad(y.sum(), x, create_graph=True)[0]
    return y_prime + y


# ---------------------------------------------------------------------------
# 4. La perte                    
# ---------------------------------------------------------------------------
def pinn_loss(network: nn.Module, x: SamplePoints) -> torch.Tensor:
    """Renvoie un SCALAIRE : moyenne(r^2) + (y(0) - 1)^2.

    """
    residual_from_ode = ode_residual(network, x)
    mean_squared_residual = torch.mean(residual_from_ode**2)
    y_at_initial_point = network(torch.tensor([[INITIAL_POINT]], dtype=DTYPE))
    initial_condition_loss = torch.mean((y_at_initial_point - INITIAL_VALUE) ** 2)
    general_loss = mean_squared_residual + initial_condition_loss
    return general_loss


# ---------------------------------------------------------------------------
# 5. La boucle d'entraînement    TODO 3
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    x: SamplePoints,
    n_epochs: int = 5000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimise pinn_loss avec Adam. Renvoie l'historique de la perte.

    Une itération = toujours les mêmes 4 étapes :
        1. remettre les gradients à zéro       optimizer.zero_grad()
        2. calculer la perte                   loss = pinn_loss(...)
        3. calculer d(perte)/d(poids)          loss.backward()
        4. mettre à jour les poids             optimizer.step()

    """
    optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    loss_history: list[float] = []

    for epoch in range(n_epochs):
        optimizer.zero_grad()
        loss = pinn_loss(network, x)
        loss.backward()
        optimizer.step()

        # Affichage de temps en temps :
        loss_history.append(loss.item())
        if epoch % 500 == 0:
            print(f"  epoch {epoch:5d}   perte = {loss.item():.3e}")

    return loss_history


# ---------------------------------------------------------------------------
# 6. La vérification
# ---------------------------------------------------------------------------
def max_error_against_exact_solution(network: nn.Module, n_test_points: int = 201) -> float:
    """Erreur max |y(x; w, b) - exp(-x)| sur des points de TEST, différents des
    points de collocation : on vérifie que le réseau a appris la fonction
    partout, pas seulement là où on l'a contraint."""
    x_test = torch.linspace(0.0, X_MAX, n_test_points, dtype=DTYPE).reshape(-1, 1)
    with torch.no_grad():  # évaluation seulement : pas besoin de graphe
        prediction = network(x_test)
    return (prediction - exact_solution(x_test)).abs().max().item()


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}")

    network = make_network()
    x_collocation = make_sample_points(n_points=50)

    print(f"Erreur max AVANT entraînement : {max_error_against_exact_solution(network):.3e}")
    train(network, x_collocation)
    print(f"Erreur max APRÈS entraînement : {max_error_against_exact_solution(network):.3e}")


if __name__ == "__main__":
    main()
