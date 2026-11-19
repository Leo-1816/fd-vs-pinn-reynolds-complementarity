.. _sec-fd-sans-cavitation:

Différences finies
==================

Le problème
-----------

On résout l'équation de Reynolds :eq:`eq-reynolds` sur un intervalle
:math:`[X_{in}, X_{out}]`, avec une pression nulle aux deux bords :

.. math::

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   = \frac{\mathrm{d}H}{\mathrm{d}X},
   \qquad P(X_{in}) = P(X_{out}) = 0 .

Le film est supposé plein partout (:math:`\theta = 0`) : il n'y a ni
cavitation ni sous-alimentation, et :math:`P` est la seule inconnue.

La discrétisation
-----------------

On développe la dérivée :

.. math::

   H^3 P'' + 3 H^2 H' P' = H', \qquad H' = X .

Le domaine est découpé en :math:`n` points réguliers :math:`X_i`, espacés de
:math:`\Delta X`. En chaque point intérieur, les dérivées sont remplacées par
des différences centrées :

.. math::

   P'' \approx \frac{P_{i-1} - 2 P_i + P_{i+1}}{\Delta X^2}, \qquad
   P' \approx \frac{P_{i+1} - P_{i-1}}{2 \Delta X} .

Chaque point intérieur donne ainsi une équation linéaire reliant
:math:`P_{i-1}`, :math:`P_i` et :math:`P_{i+1}`. Les deux bords donnent
:math:`P_0 = 0` et :math:`P_{n-1} = 0`. On obtient un système
:math:`A P = b`, avec :math:`A` tridiagonale, résolu directement en
double précision.

.. literalinclude:: /../src/fd/reynolds_1d.py
   :pyobject: solve


