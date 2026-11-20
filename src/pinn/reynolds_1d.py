"""PINN for 1D Reynolds without cavitation (report, eq. 2.7):

    d/dX (H³ dP/dX) = dH/dX   on [X_IN, X_OUT],   P(X_IN) = P(X_OUT) = 0,
    with H(X) = 1 + X²/2.

Same approach as first_pinn_ode.py, with two differences:
- the equation is of second order: we take derivatives twice with autograd;
- two boundary conditions (one at each end) instead of one initial condition.

Domain: [Xa, Xb] of the analytical solution for HB = 1.1 (imposed boundaries,
as for FD). The analytical pressure is ONLY used for checking.

Precision: float64, for the same reason as in first_pinn_ode.py.
"""

import numpy as np
import torch
from torch import nn

from analytical_solution import solution_1d as analytical

DTYPE = torch.float64
SEED = 0
BOUNDARY_PENALTY = 10.0  # weight of the boundary terms in the loss

# ---------------------------------------------------------------------------
# 1. The problem
# ---------------------------------------------------------------------------
HB = 1.1
_REFERENCE = analytical.solve(HB, np.array([0.0]))
X_IN = _REFERENCE.Xa
X_OUT = _REFERENCE.Xb

SamplePoints = torch.Tensor    # column of X values, shape (n_points, 1)
ColumnValues = torch.Tensor    # matching values, shape (n_points, 1)


def film_thickness(X: SamplePoints) -> ColumnValues:
    """H(X) = 1 + X²/2."""
    return 1.0 + 0.5 * X**2


def exact_pressure(X: SamplePoints) -> ColumnValues:
    """Analytical pressure on [Xa, Xb]. Only used for checking."""
    P = analytical.pressure_from_outlet(X.detach().numpy(), HB)
    return torch.as_tensor(P, dtype=DTYPE)


def make_sample_points(n_points: int) -> SamplePoints:
    """Evenly spaced points on [X_IN, X_OUT], shape (n_points, 1), with requires_grad."""
    X = torch.linspace(X_IN, X_OUT, n_points, dtype=DTYPE).reshape(-1, 1)
    return X.requires_grad_(True)


# ---------------------------------------------------------------------------
# 2. The network
# ---------------------------------------------------------------------------
def make_network(hidden_width: int = 20) -> nn.Module:
    """X -> P, two tanh hidden layers (non-zero second derivative, unlike ReLU)."""
    return nn.Sequential(
        nn.Linear(1, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, 1),
    ).to(DTYPE)


# ---------------------------------------------------------------------------
# 3. The Reynolds residual
# ---------------------------------------------------------------------------
def reynolds_residual(network: nn.Module, X: SamplePoints) -> ColumnValues:
    """Returns r(X) = d/dX (H³ dP/dX) − dH/dX, shape (n_points, 1).

    Steps: P, then dP/dX with autograd, then the flux H³ dP/dX, then its
    derivative with autograd. dH/dX also comes from autograd.
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
# 4. The loss
# ---------------------------------------------------------------------------
def pinn_loss(network: nn.Module, X: SamplePoints) -> torch.Tensor:
    """Returns a SCALAR: mean(r²) + weight * (P(X_IN)² + P(X_OUT)²)."""
    residual = reynolds_residual(network, X)
    P_in = network(torch.tensor([[X_IN]], dtype=DTYPE))
    P_out = network(torch.tensor([[X_OUT]], dtype=DTYPE))
    loss = torch.mean(residual**2) + BOUNDARY_PENALTY*P_in**2 + BOUNDARY_PENALTY*P_out**2
    return loss


# ---------------------------------------------------------------------------
# 5. The training loop
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    X: SamplePoints,
    n_epochs: int = 5000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimises pinn_loss with Adam. Returns the loss history."""
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
# 6. The check
# ---------------------------------------------------------------------------
def max_error_against_exact_pressure(network: nn.Module, n_test_points: int = 201) -> float:
    """Max error |P(X; w, b) − P_analytical| at test points."""
    X_test = torch.linspace(X_IN, X_OUT, n_test_points, dtype=DTYPE).reshape(-1, 1)
    with torch.no_grad():
        prediction = network(X_test)
    return (prediction - exact_pressure(X_test)).abs().max().item()


def pressure_and_gradient(network: nn.Module, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """P and dP/dX (autograd) of the network on the grid X, as numpy (for friction and load)."""
    X_column = torch.as_tensor(X, dtype=DTYPE).reshape(-1, 1).requires_grad_(True)
    P = network(X_column)
    dP_dX = torch.autograd.grad(P.sum(), X_column)[0]
    return P.detach().numpy().ravel(), dP_dX.numpy().ravel()


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}, Hb = {HB}, domain = [{X_IN:.4f}, {X_OUT:.4f}]")

    network = make_network()
    X_collocation = make_sample_points(n_points=50)

    print(f"Max error BEFORE training: {max_error_against_exact_pressure(network):.3e}")
    train(network, X_collocation)
    print(f"Max error AFTER training: {max_error_against_exact_pressure(network):.3e}")


if __name__ == "__main__":
    main()
