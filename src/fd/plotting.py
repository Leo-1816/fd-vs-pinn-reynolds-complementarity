"""Plotting functions for FD. The scripts in figures/ call them, then show the
figure with plt.show() (no image file is saved)."""

import matplotlib.pyplot as plt
import numpy as np

from pinn.plotting import COLOR_EXACT, COLOR_NETWORK, COLOR_TEXT_SECONDARY, style_axes

COLOR_FULL_FILM = "#dbe8f7"     # background of the full-film zone
COLOR_CAVITATION = "#fbe3d7"    # background of the cavitated zone


def plot_flooded_zones(X: np.ndarray, P: np.ndarray, Xb: float,
                       x_min: float, x_max: float) -> plt.Figure:
    """Diagram of the zones of the flooded case: P (top) and residual r (bottom),
    full-film zone [X_in, Xb] and cavitated zone [Xb, X_out]."""
    # r as the method defines it: Reynolds is solved in the film (r = 0);
    # in the cavitated zone P = 0, so r = −dH/dX = −X.
    r = np.where(X <= Xb, 0.0, -X)
    figure, (axes_P, axes_r) = plt.subplots(2, 1, figsize=(7, 5.5), sharex=True)

    for axes in (axes_P, axes_r):
        axes.axvspan(x_min, Xb, color=COLOR_FULL_FILM, zorder=0)
        axes.axvspan(Xb, x_max, color=COLOR_CAVITATION, zorder=0)
        axes.axvline(Xb, color=COLOR_TEXT_SECONDARY, linewidth=1, linestyle=":")
        axes.axhline(0.0, color=COLOR_TEXT_SECONDARY, linewidth=0.8)
        style_axes(axes)
        axes.grid(False)

    axes_P.plot(X, P, color=COLOR_EXACT, linewidth=2)
    axes_P.set_ylabel("P")
    axes_P.set_title(f"Flooded case: the two zones (X_in = {X[0]:g}, off the plot)",
                     loc="left")
    top = 1.15 * P.max()
    axes_P.set_ylim(-0.1 * P.max(), top)
    axes_P.text(0.5 * (x_min + Xb), 0.88 * top, "full film\nP > 0,  r = 0",
                ha="center", va="top", color=COLOR_EXACT)
    axes_P.text(0.5 * (Xb + x_max), 0.88 * top, "cavitated zone\nP = 0,  r < 0",
                ha="center", va="top", color=COLOR_NETWORK)
    axes_P.annotate(f"X_b = {Xb:.3f}\nP = dP/dX = 0", xy=(Xb, 0.0), xytext=(Xb + 0.15, 0.45 * top),
                    color=COLOR_TEXT_SECONDARY, arrowprops={"arrowstyle": "->",
                                                            "color": COLOR_TEXT_SECONDARY})

    axes_r.plot(X, r, color=COLOR_NETWORK, linewidth=2)
    axes_r.set_ylabel("r = (H³P')' − H'")
    axes_r.set_xlabel("X")
    axes_r.set_title("Reynolds residual: zero in the film, negative (= −dH/dX) in the cavitated zone",
                     loc="left", fontsize="medium", color=COLOR_TEXT_SECONDARY)
    axes_r.set_xlim(x_min, x_max)

    figure.tight_layout()
    return figure
