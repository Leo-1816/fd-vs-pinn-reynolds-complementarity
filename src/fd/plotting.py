"""Fonctions de tracé pour la FD. Les scripts de figures/ les appellent puis
affichent la figure avec plt.show() (aucun fichier image enregistré)."""

import matplotlib.pyplot as plt
import numpy as np

from pinn.plotting import COLOR_EXACT, COLOR_NETWORK, COLOR_TEXT_SECONDARY, style_axes

COLOR_FULL_FILM = "#dbe8f7"     # fond de la zone de film plein
COLOR_CAVITATION = "#fbe3d7"    # fond de la zone cavitée


def plot_flooded_zones(X: np.ndarray, P: np.ndarray, Xb: float,
                       x_min: float, x_max: float) -> plt.Figure:
    """Schéma des zones du cas noyé : P (en haut) et résidu r (en bas),
    zone de film plein [X_in, Xb] et zone cavitée [Xb, X_out]."""
    # r tel que la méthode le définit : Reynolds résolue dans le film (r = 0) ;
    # en zone cavitée P = 0, donc r = −dH/dX = −X.
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
    axes_P.set_title(f"Cas noyé : zones et complémentarité (X_in = {X[0]:g}, hors cadre à gauche)",
                     loc="left")
    top = 1.15 * P.max()
    axes_P.set_ylim(-0.1 * P.max(), top)
    axes_P.text(0.5 * (x_min + Xb), 0.88 * top, "film plein\nP > 0,  r = 0",
                ha="center", va="top", color=COLOR_EXACT)
    axes_P.text(0.5 * (Xb + x_max), 0.88 * top, "zone cavitée\nP = 0,  r < 0",
                ha="center", va="top", color=COLOR_NETWORK)
    axes_P.annotate(f"X_b = {Xb:.3f}\nP = dP/dX = 0", xy=(Xb, 0.0), xytext=(Xb + 0.15, 0.45 * top),
                    color=COLOR_TEXT_SECONDARY, arrowprops={"arrowstyle": "->",
                                                            "color": COLOR_TEXT_SECONDARY})

    axes_r.plot(X, r, color=COLOR_NETWORK, linewidth=2)
    axes_r.set_ylabel("r = (H³P')' − H'")
    axes_r.set_xlabel("X")
    axes_r.set_title("Résidu de Reynolds : nul dans le film, négatif (= −dH/dX) en zone cavitée",
                     loc="left", fontsize="medium", color=COLOR_TEXT_SECONDARY)
    axes_r.set_xlim(x_min, x_max)

    figure.tight_layout()
    return figure
