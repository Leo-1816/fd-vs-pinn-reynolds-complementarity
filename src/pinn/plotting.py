"""Plotting functions for the PINNs. The scripts in figures/ call them, then
show the figure with plt.show() (no image file is saved)."""

import matplotlib.pyplot as plt
import torch
from torch import nn

# Validated categorical palette (slots 1 and 2), axes and grid in neutral grey.
COLOR_EXACT = "#2a78d6"
COLOR_NETWORK = "#eb6834"
COLOR_TEXT_SECONDARY = "#5f5e5a"
COLOR_GRID = "#e4e3dd"


def style_axes(axes: plt.Axes) -> None:
    axes.grid(True, color=COLOR_GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    for side in ("top", "right"):
        axes.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axes.spines[side].set_color(COLOR_TEXT_SECONDARY)
    axes.tick_params(colors=COLOR_TEXT_SECONDARY)


def plot_network_vs_exact_solution(
    network: nn.Module,
    exact_solution,
    x_points: torch.Tensor,
    y_points: torch.Tensor,
    x_min: float,
    x_max: float,
    title: str,
    network_label: str,
    points_label: str,
    n_plot_points: int = 401,
) -> plt.Figure:
    """Top: network vs exact solution + points (x_points, y_points).
    Bottom: absolute error on a log scale.

    The points are passed explicitly: for a PINN they are the collocation
    points (network values), for a supervised fit they are the training data."""
    x_plot = torch.linspace(x_min, x_max, n_plot_points, dtype=x_points.dtype).reshape(-1, 1)
    with torch.no_grad():
        y_network = network(x_plot)
    y_exact = exact_solution(x_plot)
    absolute_error = (y_network - y_exact).abs()
    print(f"Max error on [{x_min}, {x_max}]: {absolute_error.max().item():.3e}")

    x_plot_np = x_plot.squeeze().numpy()
    figure, (axes_solution, axes_error) = plt.subplots(
        2, 1, figsize=(7, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )

    axes_solution.plot(
        x_plot_np, y_exact.squeeze().numpy(),
        color=COLOR_EXACT, linewidth=2, label="exact solution",
    )
    axes_solution.plot(
        x_plot_np, y_network.squeeze().numpy(),
        color=COLOR_NETWORK, linewidth=2, linestyle="--", label=network_label,
    )
    axes_solution.plot(
        x_points.detach().squeeze().numpy(), y_points.detach().squeeze().numpy(),
        linestyle="none", marker="o", markersize=4, markerfacecolor="white",
        markeredgecolor=COLOR_NETWORK, label=points_label,
    )
    axes_solution.set_ylabel("y")
    axes_solution.set_title(title, loc="left")
    axes_solution.legend(frameon=False)
    style_axes(axes_solution)

    axes_error.semilogy(x_plot_np, absolute_error.squeeze().numpy(), color=COLOR_NETWORK, linewidth=2)
    axes_error.set_xlabel("x")
    axes_error.set_ylabel("|y(x; w, b) - y exact|")
    axes_error.set_title(
        f"Absolute error (max = {absolute_error.max().item():.1e})",
        loc="left", fontsize="medium", color=COLOR_TEXT_SECONDARY,
    )
    style_axes(axes_error)

    figure.tight_layout()
    return figure


def plot_pinn_vs_fd_pressure(X, P_fd, P_pinn, title: str, subtitle: str) -> plt.Figure:
    """Top: FD vs PINN pressure. Bottom: absolute gap on a log scale.

    X, P_fd, P_pinn: numpy arrays of the same shape (n,)."""
    figure, (axes_pressure, axes_gap) = plt.subplots(
        2, 1, figsize=(7, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )

    axes_pressure.plot(X, P_fd, color=COLOR_EXACT, linewidth=2, label="FD")
    axes_pressure.plot(X, P_pinn, color=COLOR_NETWORK, linewidth=2, linestyle="--",
                       label="PINN : P(X; w, b)")
    axes_pressure.set_ylabel("P")
    axes_pressure.set_title(title, loc="left")
    axes_pressure.legend(frameon=False)
    style_axes(axes_pressure)

    axes_gap.semilogy(X, abs(P_pinn - P_fd), color=COLOR_NETWORK, linewidth=2)
    axes_gap.set_xlabel("X")
    axes_gap.set_ylabel("|P PINN − P FD|")
    axes_gap.set_title(subtitle, loc="left", fontsize="medium", color=COLOR_TEXT_SECONDARY)
    style_axes(axes_gap)

    figure.tight_layout()
    return figure
