"""First steps with torch.autograd: compare derivatives computed by hand,
by automatic differentiation, and by centred finite differences.

Part 1: analytic function f(x) = x^2 sin(x).


Everything runs in float64: we want to check agreement down to machine
precision, which float32 (~1e-7 noise) would hide.


"""



import torch

DTYPE = torch.float64
SEED = 0

# Type aliases: a column of sample points, shape (n_points, 1),
# and the matching column of values/derivatives.
SamplePoints = torch.Tensor # x abscisses 
ColumnValues = torch.Tensor  # y function values


# ---------------------------------------------------------------------------
# autograd
# ---------------------------------------------------------------------------
def autograd_first_and_second_derivative(
    function_values: ColumnValues, sample_points: SamplePoints
) -> tuple[ColumnValues, ColumnValues]:
    """Return (dy/dx, d2y/dx2) at each sample point using torch.autograd.grad.

    create_graph=True is necessary so that it can
    be differentiated again (this is what a PINN needs for y'').
    """
    first_derivative = torch.autograd.grad(
        function_values.sum(), sample_points, create_graph=True
    )[0]
    second_derivative = torch.autograd.grad(
        first_derivative.sum(), sample_points, create_graph=True
    )[0]
    return first_derivative, second_derivative


# ---------------------------------------------------------------------------
# FD
# ---------------------------------------------------------------------------


def centred_finite_difference_derivatives(
    function, sample_points: SamplePoints, step: float = 1e-4
) -> tuple[ColumnValues, ColumnValues]:
    """Return (dy/dx, d2y/dx2) at each sample point using centred finite differences."""
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
# Comparison report
# ---------------------------------------------------------------------------
def make_sample_points(n_points: int = 101) -> SamplePoints:
    return torch.linspace(-3.0, 3.0, n_points, dtype=DTYPE, requires_grad=True).reshape(-1, 1)


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
    x = make_sample_points()
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

    
    print("\nExpected: hand vs autograd ~1e-15 (exact),")
    print("          hand vs FD ~1e-8  (truncation).")


if __name__ == "__main__":
    main()
