.. _sec-pinn-sans-cavitation:

PINN
====

Le problème est le même que pour les différences finies
(:ref:`sec-fd-sans-cavitation`) : l'équation :eq:`eq-reynolds` sur
:math:`[X_a, X_b]`, avec :math:`P = 0` aux deux bords. La démarche est celle
du premier PINN (:ref:`sec-premiere-edo`), avec deux différences : l'équation
est d'ordre 2, et il y a une condition à chaque bord.

Le résidu
---------

Le réseau donne :math:`P(X; w, b)`. On calcule :math:`\mathrm{d}P/\mathrm{d}X`
par autograd, on forme le débit de Poiseuille :math:`H^3\,\mathrm{d}P/\mathrm{d}X`,
puis on le dérive une seconde fois. On garde ainsi la forme conservative de
l'équation, sans la développer :

.. math::

   r(X) = \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   - \frac{\mathrm{d}H}{\mathrm{d}X} .

.. literalinclude:: /../src/pinn/reynolds_1d.py
   :pyobject: reynolds_residual

La perte
--------

La perte additionne la moyenne de :math:`r^2` sur les points de collocation et
les carrés de la pression aux deux bords, multipliés par un poids
:math:`\lambda` :

.. math::

   \mathcal{L}(w, b) = \frac{1}{N} \sum_{i=1}^{N} r(X_i)^2
   + \lambda \left( P(X_a)^2 + P(X_b)^2 \right) .

.. literalinclude:: /../src/pinn/reynolds_1d.py
   :pyobject: pinn_loss

Le poids :math:`\lambda` équilibre les deux termes : la pression est petite
devant le second membre :math:`\mathrm{d}H/\mathrm{d}X`, et sans poids les
conditions aux limites sont mal respectées. L'entraînement (Adam) est
identique à celui du premier PINN.

La validation
-------------

Comme pour les différences finies, le réseau est comparé à la pression
analytique :eq:`eq-pression-analytique` sur des points de test distincts des
points de collocation.
