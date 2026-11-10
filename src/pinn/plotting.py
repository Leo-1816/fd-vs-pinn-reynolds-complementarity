"""Fonctions de tracé pour les PINN. Les scripts de figures/ les appellent
puis affichent la figure avec plt.show() (aucun fichier image enregistré)."""

import matplotlib.pyplot as plt
import torch
from torch import nn

# Palette catégorielle validée (slots 1 et 2), axes et grille en gris neutre.
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


def plot_pinn_vs_exact_solution(
    network: nn.Module,
    exact_solution,
    x_collocation: torch.Tensor,
    x_min: float,
    x_max: float,
    title: str,
    n_plot_points: int = 401,
) -> plt.Figure:
    """En haut : réseau vs solution exacte + points de collocation.
    En bas : erreur absolue en échelle log."""
    x_plot = torch.linspace(x_min, x_max, n_plot_points, dtype=x_collocation.dtype).reshape(-1, 1)
    with torch.no_grad():
        y_network = network(x_plot)
        y_collocation = network(x_collocation)
    y_exact = exact_solution(x_plot)
    absolute_error = (y_network - y_exact).abs()
    print(f"Erreur max sur [{x_min}, {x_max}] : {absolute_error.max().item():.3e}")

    x_plot_np = x_plot.squeeze().numpy()
    figure, (axes_solution, axes_error) = plt.subplots(
        2, 1, figsize=(7, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )

    axes_solution.plot(
        x_plot_np, y_exact.squeeze().numpy(),
        color=COLOR_EXACT, linewidth=2, label="solution exacte",
    )
    axes_solution.plot(
        x_plot_np, y_network.squeeze().numpy(),
        color=COLOR_NETWORK, linewidth=2, linestyle="--", label="PINN : y(x; w, b)",
    )
    axes_solution.plot(
        x_collocation.detach().squeeze().numpy(), y_collocation.squeeze().numpy(),
        linestyle="none", marker="o", markersize=4, markerfacecolor="white",
        markeredgecolor=COLOR_NETWORK, label=f"{len(x_collocation)} points de collocation",
    )
    axes_solution.set_ylabel("y")
    axes_solution.set_title(title, loc="left")
    axes_solution.legend(frameon=False)
    style_axes(axes_solution)

    axes_error.semilogy(x_plot_np, absolute_error.squeeze().numpy(), color=COLOR_NETWORK, linewidth=2)
    axes_error.set_xlabel("x")
    axes_error.set_ylabel("|y(x; w, b) - y exacte|")
    style_axes(axes_error)

    figure.tight_layout()
    return figure
