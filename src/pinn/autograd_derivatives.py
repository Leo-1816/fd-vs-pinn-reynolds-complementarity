"""First steps with torch.autograd: compare derivatives computed by hand,
by automatic differentiation, and by centred finite differences.

Part 1: analytic function f(x) = x^2 sin(x).
Part 2: one-hidden-layer network u(x) = W2 . tanh(W1 x + b1) + b2.

Everything runs in float64: we want to check agreement down to machine
precision, which float32 (~1e-7 noise) would hide.

Run: uv run python src/pinn/autograd_derivatives.py
"""

from dataclasses import dataclass

import torch

DTYPE = torch.float64
SEED = 0

# Type aliases: a column of sample points, shape (n_points, 1),
# and the matching column of values/derivatives.
SamplePoints = torch.Tensor
ColumnValues = torch.Tensor


# ---------------------------------------------------------------------------
# Generic autograd helper
# ---------------------------------------------------------------------------
def autograd_first_and_second_derivative(
    function_values: ColumnValues, sample_points: SamplePoints
) -> tuple[ColumnValues, ColumnValues]:
    """Return (dy/dx, d2y/dx2) at each sample point using torch.autograd.grad.

    The points are independent of each other, so summing the outputs gives
    one scalar whose gradient w.r.t. x_i is exactly dy_i/dx_i.
    create_graph=True keeps the graph of the first derivative so that it can
    be differentiated again (this is what a PINN needs for y'').
    """
    first_derivative = torch.autograd.grad(
        function_values.sum(), sample_points, create_graph=True
    )[0]
    second_derivative = torch.autograd.grad(
        first_derivative.sum(), sample_points, create_graph=True
    )[0]
    return first_derivative, second_derivative


def centred_finite_difference_derivatives(
    function, sample_points: SamplePoints, step: float = 1e-4
) -> tuple[ColumnValues, ColumnValues]:
    """Independent sanity check: centred differences, O(step^2) accurate."""
    with torch.no_grad():
        f_plus = function(sample_points + step)
        f_centre = function(sample_points)
        f_minus = function(sample_points - step)
    first_derivative = (f_plus - f_minus) / (2.0 * step)
    second_derivative = (f_plus - 2.0 * f_centre + f_minus) / step**2
    return first_derivative, second_derivative


# ---------------------------------------------------------------------------
# Part 1: analytic function
# ---------------------------------------------------------------------------
def analytic_function(x: SamplePoints) -> ColumnValues:
    """f(x) = x^2 sin(x)."""
    return x**2 * torch.sin(x)


def analytic_function_first_derivative_by_hand(x: SamplePoints) -> ColumnValues:
    """f'(x) = 2x sin(x) + x^2 cos(x)."""
    return 2.0 * x * torch.sin(x) + x**2 * torch.cos(x)


def analytic_function_second_derivative_by_hand(x: SamplePoints) -> ColumnValues:
    """f''(x) = (2 - x^2) sin(x) + 4x cos(x)."""
    return (2.0 - x**2) * torch.sin(x) + 4.0 * x * torch.cos(x)


# ---------------------------------------------------------------------------
# Part 2: one-hidden-layer tanh network, written explicitly
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TanhNetworkParameters:
    """u(x) = W2 . tanh(W1 x + b1) + b2, scalar input and output.

    Shapes: input_weights (1, H), input_biases (1, H),
            output_weights (H, 1), output_bias (1,).
    """

    input_weights: torch.Tensor
    input_biases: torch.Tensor
    output_weights: torch.Tensor
    output_bias: torch.Tensor


def make_random_tanh_network(hidden_width: int, seed: int = SEED) -> TanhNetworkParameters:
    generator = torch.Generator().manual_seed(seed)

    def draw(*shape: int) -> torch.Tensor:
        return torch.randn(*shape, generator=generator, dtype=DTYPE)

    return TanhNetworkParameters(
        input_weights=draw(1, hidden_width),
        input_biases=draw(1, hidden_width),
        output_weights=draw(hidden_width, 1),
        output_bias=draw(1),
    )


def tanh_network(params: TanhNetworkParameters, x: SamplePoints) -> ColumnValues:
    pre_activation = x @ params.input_weights + params.input_biases  # (n, H)
    return torch.tanh(pre_activation) @ params.output_weights + params.output_bias


def tanh_network_derivatives_by_hand(
    params: TanhNetworkParameters, x: SamplePoints
) -> tuple[ColumnValues, ColumnValues]:
    """With z = W1 x + b1 and s = tanh(z), using tanh' = 1 - tanh^2:

        u'(x)  = sum_k W2_k * W1_k   * (1 - s_k^2)
        u''(x) = sum_k W2_k * W1_k^2 * (-2 s_k (1 - s_k^2))

    (the bias b2 disappears, b1 only enters through z).
    """
    pre_activation = x @ params.input_weights + params.input_biases  # (n, H)
    activation = torch.tanh(pre_activation)
    tanh_derivative = 1.0 - activation**2
    tanh_second_derivative = -2.0 * activation * tanh_derivative

    first_derivative = (params.input_weights * tanh_derivative) @ params.output_weights
    second_derivative = (
        params.input_weights**2 * tanh_second_derivative
    ) @ params.output_weights
    return first_derivative, second_derivative


# ---------------------------------------------------------------------------
# Comparison report
# ---------------------------------------------------------------------------
def make_sample_points(n_points: int = 101) -> SamplePoints:
    return torch.linspace(-3.0, 3.0, n_points, dtype=DTYPE).reshape(-1, 1)


def max_abs_error(a: ColumnValues, b: ColumnValues) -> float:
    return (a - b).abs().max().item()


def print_comparison(
    title: str,
    by_hand: tuple[ColumnValues, ColumnValues],
    by_autograd: tuple[ColumnValues, ColumnValues],
    by_finite_difference: tuple[ColumnValues, ColumnValues],
) -> None:
    print(f"\n{title}")
    print(f"  {'':6s} {'|hand - autograd|':>20s} {'|hand - FD|':>14s}")
    for order, label in enumerate(["y'", "y''"]):
        print(
            f"  {label:6s} {max_abs_error(by_hand[order], by_autograd[order]):20.2e}"
            f" {max_abs_error(by_hand[order], by_finite_difference[order]):14.2e}"
        )


def main() -> None:
    print(f"seed = {SEED}, dtype = {DTYPE}")

    # Part 1
    x = make_sample_points().requires_grad_(True)
    print_comparison(
        "Part 1: f(x) = x^2 sin(x)",
        by_hand=(
            analytic_function_first_derivative_by_hand(x),
            analytic_function_second_derivative_by_hand(x),
        ),
        by_autograd=autograd_first_and_second_derivative(analytic_function(x), x),
        by_finite_difference=centred_finite_difference_derivatives(
            analytic_function, x.detach()
        ),
    )

    # Part 2
    params = make_random_tanh_network(hidden_width=5)
    x = make_sample_points().requires_grad_(True)
    print_comparison(
        "Part 2: u(x) = W2 . tanh(W1 x + b1) + b2  (hidden width 5)",
        by_hand=tanh_network_derivatives_by_hand(params, x),
        by_autograd=autograd_first_and_second_derivative(tanh_network(params, x), x),
        by_finite_difference=centred_finite_difference_derivatives(
            lambda points: tanh_network(params, points), x.detach()
        ),
    )
    print("\nExpected: hand vs autograd ~1e-15 (exact up to rounding),")
    print("          hand vs FD ~1e-8 for y' and ~1e-6 for y'' (truncation + rounding).")


if __name__ == "__main__":
    main()
