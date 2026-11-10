import torch

from pinn.autograd_derivatives import (
    analytic_function,
    analytic_function_first_derivative_by_hand,
    analytic_function_second_derivative_by_hand,
    autograd_first_and_second_derivative,
    make_random_tanh_network,
    make_sample_points,
    tanh_network,
    tanh_network_derivatives_by_hand,
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


def test_tanh_network_hand_derivatives_match_autograd() -> None:
    for seed in (0, 1, 2):
        params = make_random_tanh_network(hidden_width=5, seed=seed)
        x = make_sample_points().requires_grad_(True)
        first, second = autograd_first_and_second_derivative(tanh_network(params, x), x)
        first_by_hand, second_by_hand = tanh_network_derivatives_by_hand(params, x)
        torch.testing.assert_close(first, first_by_hand, atol=TOLERANCE, rtol=0)
        torch.testing.assert_close(second, second_by_hand, atol=TOLERANCE, rtol=0)
