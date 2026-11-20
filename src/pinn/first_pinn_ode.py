"""First PINN: solve y'(x) = -y(x) on [0, X_MAX], with y(0) = 1.

Exact solution: y(x) = exp(-x) (ONLY used for checking, never in the loss).

------------------------------------------------------------------------------
The idea in one sentence
------------------------------------------------------------------------------
We do not look for y(x) as a list of values (as in FD). We look for a neural
network y(x; w, b) whose weights w and biases b make the equation hold. So
"solve the ODE" becomes "minimise a loss":

    loss(w, b) =  mean over the x_i of [ y'(x_i; w, b) + y(x_i; w, b) ]^2   <- ODE residual
                + [ y(0; w, b) - 1 ]^2                                      <- initial condition

If the loss is 0, then y' + y = 0 at all x_i AND y(0) = 1:
y(x; w, b) is (approximately) the solution. We never gave exp(-x) to the
network, only the equation.

The x_i are the "collocation points": the places where we check the
equation. They play a role similar to the nodes in FD.

------------------------------------------------------------------------------
What we reuse from autograd_derivatives.py
------------------------------------------------------------------------------
- x.requires_grad_(True) on the collocation points, so we can take the
  derivative of the network output with respect to x.
- torch.autograd.grad(..., create_graph=True) to get y'(x).
  create_graph=True is essential here: the loss contains y', and we then take
  the derivative of the loss with respect to the weights w and biases b
  (backward). Without the graph, w and b get no gradient.

------------------------------------------------------------------------------
Plan of the file
------------------------------------------------------------------------------
1. The problem
2. The network
3. The ODE residual
4. The loss
5. The training loop
6. The check

Precision: float64. The problem is tiny, so the cost is negligible, and the
float32 rounding error (~1e-7) does not mix with the PINN error we measure.
"""

import torch
from torch import nn

DTYPE = torch.float64
SEED = 0

# ---------------------------------------------------------------------------
# 1. The problem
# ---------------------------------------------------------------------------
X_MAX = 2.0
INITIAL_POINT = 0.0
INITIAL_VALUE = 1.0

# Types: a column of points, shape (n_points, 1), and the matching values.
SamplePoints = torch.Tensor
ColumnValues = torch.Tensor


def exact_solution(x: SamplePoints) -> ColumnValues:
    """y(x) = exp(-x). Only used for checking."""
    return torch.exp(-x)


def make_sample_points(n_points: int) -> SamplePoints:
    """Evenly spaced points on [0, X_MAX], shape (n_points, 1),
    with requires_grad so that autograd can compute y'(x)."""
    x = torch.linspace(0.0, X_MAX, n_points, dtype=DTYPE).reshape(-1, 1)
    return x.requires_grad_(True)


# ---------------------------------------------------------------------------
# 2. The network
# ---------------------------------------------------------------------------
def make_network(hidden_width: int = 20) -> nn.Module:
    """x (1 value) -> y (1 value), two tanh hidden layers.

    tanh rather than ReLU: ReLU is piecewise linear, so its second derivative
    is zero almost everywhere. Here we only need y', but we get into the habit
    now (for equations with y'', ReLU would fail).
    """
    return nn.Sequential(
        nn.Linear(1, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, hidden_width),
        nn.Tanh(),
        nn.Linear(hidden_width, 1),
    ).to(DTYPE)


# ---------------------------------------------------------------------------
# 3. The ODE residual
# ---------------------------------------------------------------------------
def ode_residual(network: nn.Module, x: SamplePoints) -> ColumnValues:
    """Returns r(x) = y'(x) + y(x), shape (n_points, 1)."""
    y = network(x)
    y_prime = torch.autograd.grad(y.sum(), x, create_graph=True)[0]
    return y_prime + y


# ---------------------------------------------------------------------------
# 4. The loss
# ---------------------------------------------------------------------------
def pinn_loss(network: nn.Module, x: SamplePoints) -> torch.Tensor:
    """Returns a SCALAR: mean(r^2) + (y(0) - 1)^2."""
    residual_from_ode = ode_residual(network, x)
    mean_squared_residual = torch.mean(residual_from_ode**2)
    y_at_initial_point = network(torch.tensor([[INITIAL_POINT]], dtype=DTYPE))
    initial_condition_loss = torch.mean((y_at_initial_point - INITIAL_VALUE) ** 2)
    general_loss = mean_squared_residual + initial_condition_loss
    return general_loss


# ---------------------------------------------------------------------------
# 5. The training loop
# ---------------------------------------------------------------------------
def train(
    network: nn.Module,
    x: SamplePoints,
    n_epochs: int = 5000,
    learning_rate: float = 1e-3,
) -> list[float]:
    """Minimises pinn_loss with Adam. Returns the loss history.

    One iteration = always the same 4 steps:
        1. set the gradients back to zero      optimizer.zero_grad()
        2. compute the loss                    loss = pinn_loss(...)
        3. compute d(loss)/d(weights)          loss.backward()
        4. update the weights                  optimizer.step()
    """
    optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    loss_history: list[float] = []

    for epoch in range(n_epochs):
        optimizer.zero_grad()
        loss = pinn_loss(network, x)
        loss.backward()
        optimizer.step()

        # Print from time to time:
        loss_history.append(loss.item())
        if epoch % 500 == 0:
            print(f"  epoch {epoch:5d}   loss = {loss.item():.3e}")

    return loss_history


# ---------------------------------------------------------------------------
# 6. The check
# ---------------------------------------------------------------------------
def max_error_against_exact_solution(network: nn.Module, n_test_points: int = 201) -> float:
    """Max error |y(x; w, b) - exp(-x)| at TEST points, different from the
    collocation points: we check that the network learned the function
    everywhere, not only where we constrained it."""
    x_test = torch.linspace(0.0, X_MAX, n_test_points, dtype=DTYPE).reshape(-1, 1)
    with torch.no_grad():  # evaluation only: no graph needed
        prediction = network(x_test)
    return (prediction - exact_solution(x_test)).abs().max().item()


def main() -> None:
    torch.manual_seed(SEED)
    print(f"seed = {SEED}, dtype = {DTYPE}")

    network = make_network()
    x_collocation = make_sample_points(n_points=50)

    print(f"Max error BEFORE training: {max_error_against_exact_solution(network):.3e}")
    train(network, x_collocation)
    print(f"Max error AFTER training: {max_error_against_exact_solution(network):.3e}")


if __name__ == "__main__":
    main()
