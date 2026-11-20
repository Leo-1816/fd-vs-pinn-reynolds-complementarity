"""PINN for 1D Reynolds, flooded case with cavitation (same problem as fd/reynolds_1d_flooded.py).

On [X_IN, X_OUT], P(X_IN) = P(X_OUT) = 0. We do not know Xb: we impose the
complementarity between the pressure and the Reynolds residual r (without θ):

    P ≥ 0,   −r ≥ 0,   P · r = 0

    - full film (P > 0)      : r = 0, Reynolds holds;
    - cavitated zone (P = 0) : r ≤ 0 is enough (penalising only P < 0 does not
      work: in the cavitated zone, r = −dH/dX ≠ 0, so the network would have to
      choose between the two).

The three conditions fit into one equation (Fischer-Burmeister, as in the
report, eq. eq-fischer-burmeister, with θ replaced by −r):

    φ(P, −r) = P − r − √(P² + r²) = 0

Source of this complementarity: HL-nets (Cheng et al., arXiv:2304.10476), eq. 5.
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
# 1. The problem
# ---------------------------------------------------------------------------
X_IN = -10.0
X_OUT = 3.0

SamplePoints = torch.Tensor    # column of X values, shape (n_points, 1)
ColumnValues = torch.Tensor    # matching values, shape (n_points, 1)


def make_sample_points(n_points: int) -> SamplePoints:
    """Evenly spaced points on [X_IN, X_OUT], shape (n_points, 1), with requires_grad."""
    X = torch.linspace(X_IN, X_OUT, n_points, dtype=DTYPE).reshape(-1, 1)
    return X.requires_grad_(True)


# ---------------------------------------------------------------------------
# 2. The network
# ---------------------------------------------------------------------------
class PressureNetwork(nn.Module):
    """X -> P. X is first scaled to [−1, 1], then three tanh hidden layers."""

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
# 3. The complementarity residual
# ---------------------------------------------------------------------------
def complementarity_residual(network: nn.Module, X: SamplePoints) -> ColumnValues:
    """Returns φ(P, −r/H³) = P − r/H³ − √(P² + (r/H³)²), shape (n_points, 1).

    r comes from reynolds_residual (pinn/reynolds_1d.py), H from film_thickness.
    Dividing by H³ > 0 keeps the sign of r, but stops r from crushing the other
    terms upstream, where H³ is about 10⁵.
    """
    r = reynolds_residual(network, X)
    H = film_thickness(X)
    P = network(X)
    r_scaled = r / H**3
    # SQRT_EPSILON: avoids an infinite derivative of √ when P = r = 0
    return P - r_scaled - torch.sqrt(P**2 + r_scaled**2 + SQRT_EPSILON)


# ---------------------------------------------------------------------------
# 4. The loss
# ---------------------------------------------------------------------------
def pinn_loss(network: nn.Module, X: SamplePoints) -> torch.Tensor:
    """Returns a SCALAR: mean(φ²) + BOUNDARY_PENALTY (P(X_IN)² + P(X_OUT)²)."""
    phi = complementarity_residual(network, X)
    P_in = network(torch.tensor([[X_IN]], dtype=DTYPE))
    P_out = network(torch.tensor([[X_OUT]], dtype=DTYPE))
    loss = torch.mean(phi**2) + BOUNDARY_PENALTY * (P_in**2 + P_out**2).squeeze()
    return loss


# ---------------------------------------------------------------------------
# 5. The training loop
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    X: SamplePoints,
    n_epochs: int = 15000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimises pinn_loss with Adam (same loop as pinn/reynolds_1d.py)."""
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
# 6. The check
# ---------------------------------------------------------------------------
def exact_solution(X: np.ndarray) -> analytical.AnalyticalSolution1D:
    """Analytical solution whose meniscus is at Xa = X_IN (see the FD flooded-case test)."""
    Hb = root_scalar(lambda h: float(analytical.pressure_from_outlet(X_IN, h)),
                     bracket=(1.0, 1.2258), method="brentq").root
    return analytical.solve(Hb, X)


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}, domain = [{X_IN}, {X_OUT}]")

    network = PressureNetwork()
    train(network, make_sample_points(n_points=400))

    X_test = np.linspace(X_IN, X_OUT, 2001)
    exact = exact_solution(X_test)
    with torch.no_grad():
        P = network(torch.as_tensor(X_test, dtype=DTYPE).reshape(-1, 1)).numpy().ravel()
    print(f"Max error on P: {np.max(np.abs(P - exact.P)):.3e}  (P max = {exact.P.max():.3f})")
    print(f"W PINN = {np.trapezoid(P, X_test):.4f}, W exact = {exact.W:.4f}")


if __name__ == "__main__":
    main()
