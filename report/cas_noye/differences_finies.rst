.. _sec-fd-cas-noye:

Différences finies : méthode de tir
===================================

Le problème
-----------

Sur :math:`[X_{in}, X_{out}]`, avec :math:`X_{in}` loin en amont pour approcher
:math:`X_a = -\infty` :

.. math::

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   = \frac{\mathrm{d}H}{\mathrm{d}X} \ \text{sur } [X_{in}, X_b],
   \qquad P = 0 \ \text{sur } [X_b, X_{out}],

avec :math:`P(X_{in}) = 0`. La frontière :math:`X_b` est inconnue : elle est
fixée par la condition de Reynolds :math:`P(X_b) = \mathrm{d}P/\mathrm{d}X(X_b) = 0`.

La méthode
----------

Pour un :math:`X_b` supposé, le solveur de :ref:`sec-fd-sans-cavitation`
donne la pression sur :math:`[X_{in}, X_b]` avec :math:`P = 0` aux deux bords.
On calcule ensuite la pente en :math:`X_b` (différence décentrée d'ordre 2) :

.. literalinclude:: /../src/fd/reynolds_1d_flooded.py
   :pyobject: outlet_slope

Si la pente est négative, :math:`X_b` est trop tôt ; si elle est positive, il
est trop tard. La méthode de Brent (``scipy.optimize.root_scalar``) ajuste
:math:`X_b` jusqu'à annuler la pente. Au-delà de :math:`X_b`, :math:`P = 0`.

La validation
-------------

Comme :math:`X_{in}` est fini, le cas résolu est très légèrement
sous-alimenté : c'est la solution analytique dont le ménisque est en
:math:`X_a = X_{in}` (:ref:`sec-solution-analytique`). On compare à cette
solution :math:`X_b`, la charge :math:`W` et la pression. Quand :math:`X_{in}`
s'éloigne, elle tend vers le cas noyé.
