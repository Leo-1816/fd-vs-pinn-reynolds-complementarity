import torch

from pinn.autograd_derivatives import (
    analytic_function,
    analytic_function_first_derivative_by_hand,
    analytic_function_second_derivative_by_hand,
    autograd_first_and_second_derivative,
    make_sample_points,
)

TOLERANCE = 1e-12


def test_analytic_function_hand_derivatives_match_autograd() -> None:
    x = make_sample_points().requires_grad_(True)
    first, second = autograd_first_and_second_derivative(analytic_function(x), x)
    torch.testing.assert_close(
        first, analytic_function_first_derivative_by_hand(x), atol=TOLERANCE, rtol=0
    )
    torch.testing.assert_close(
        second, analytic_function_second_derivative_by_hand(x), atol=TOLERANCE, rtol=0
    )

