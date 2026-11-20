"""Supervised learning: we give the network training points (x_i, sin(x_i))
and minimise the loss MSE = mean((y(x_i; w, b) - sin(x_i))^2).

The function to learn is defined in target_function(x).
To learn another function, just change that function.
"""

import math

import torch
from torch import nn

DTYPE = torch.float64
SEED = 0

# ---------------------------------------------------------------------------
# 1. The data
# ---------------------------------------------------------------------------
X_MIN = -math.pi
X_MAX = math.pi

SamplePoints = torch.Tensor   # shape (n_points, 1)
ColumnValues = torch.Tensor   # shape (n_points, 1)


# ---------------------------------------------------------
# ---------------------------------------------------------
# Function to learn
# The only thing to change to learn another function


def target_function(x: SamplePoints) -> ColumnValues:
    """The function to learn: sin(x)."""
    return torch.sin(x)

# ---------------------------------------------------------
# ---------------------------------------------------------


def make_training_data(n_points: int) -> tuple[SamplePoints, ColumnValues]:
    """Evenly spaced points on [X_MIN, X_MAX] and the matching values sin(x).
    No requires_grad: we do not take derivatives with respect to x."""
    x = torch.linspace(X_MIN, X_MAX, n_points, dtype=DTYPE).reshape(-1, 1)
    return x, target_function(x)


# ---------------------------------------------------------------------------
# 2. The network
# ---------------------------------------------------------------------------
def make_network(hidden_width: int = 20) -> nn.Module:
    """x (1 value) -> y (1 value), one tanh hidden layer of hidden_width neurons."""
    return nn.Sequential(
        nn.Linear(1, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, 1)).to(DTYPE)


# ---------------------------------------------------------------------------
# 3. The loss
# ---------------------------------------------------------------------------
def mean_squared_error_loss(
    network: nn.Module, x: SamplePoints, y_target: ColumnValues
) -> torch.Tensor:
    """Returns a SCALAR: mean of (y(x; w, b) - sin(x))^2."""

    y_pred = network(x)
    loss = torch.mean((y_pred - y_target) ** 2)
    return loss


# ---------------------------------------------------------------------------
# 4. The training loop
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    x: SamplePoints,
    y_target: ColumnValues,
    n_epochs: int = 5000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimises mean_squared_error_loss with Adam. Returns the loss history.

    Same 4 steps per iteration as for the PINN: only the loss changes.
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
            print(f"  epoch {epoch:5d}   loss = {loss.item():.3e}")

    return loss_history


# ---------------------------------------------------------------------------
# 5. The check
# ---------------------------------------------------------------------------
def max_error_against_target(network: nn.Module, n_test_points: int = 401) -> float:
    """Max error |y(x; w, b) - sin(x)| at TEST points, more numerous than the
    training points: did the network learn the function between the points,
    or only memorise the training points?"""
    x_test = torch.linspace(X_MIN, X_MAX, n_test_points, dtype=DTYPE).reshape(-1, 1)
    with torch.no_grad():
        prediction = network(x_test)
    return (prediction - target_function(x_test)).abs().max().item()


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}")

    network = make_network()
    x_train, y_train = make_training_data(n_points=50)

    print(f"Max error BEFORE training: {max_error_against_target(network):.3e}")
    train(network, x_train, y_train)
    print(f"Max error AFTER training: {max_error_against_target(network):.3e}")




if __name__ == "__main__":
    main()
