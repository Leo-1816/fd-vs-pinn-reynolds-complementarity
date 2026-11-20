.. _sec-pinn-sans-cavitation:

PINN
====

The problem is the same as for finite differences
(:ref:`sec-fd-sans-cavitation`): the equation :eq:`eq-reynolds` on
:math:`[X_a, X_b]`, with :math:`P = 0` at both ends. We follow the first PINN
(:ref:`sec-premiere-edo`), with two differences: the equation is of second
order, and there is one condition at each end.

The residual
------------

The network gives :math:`P(X; w, b)`. We compute :math:`\mathrm{d}P/\mathrm{d}X`
with autograd, we build the Poiseuille flow :math:`H^3\,\mathrm{d}P/\mathrm{d}X`,
then we take its derivative a second time. This way we keep the conservative
form of the equation, without expanding it:

.. math::

   r(X) = \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   - \frac{\mathrm{d}H}{\mathrm{d}X} .

.. literalinclude:: /../src/pinn/reynolds_1d.py
   :pyobject: reynolds_residual

The loss
--------

The loss adds the mean of :math:`r^2` over the collocation points and the
squares of the pressure at both ends, multiplied by a weight :math:`\lambda`:

.. math::

   \mathcal{L}(w, b) = \frac{1}{N} \sum_{i=1}^{N} r(X_i)^2
   + \lambda \left( P(X_a)^2 + P(X_b)^2 \right) .

.. literalinclude:: /../src/pinn/reynolds_1d.py
   :pyobject: pinn_loss

The weight :math:`\lambda` balances the two terms. The pressure is small
compared with the right-hand side :math:`\mathrm{d}H/\mathrm{d}X`. Without a
weight, the network pays little attention to the ends, and the boundary
conditions are poorly met. Training (Adam) is the same as for the first PINN.

Validation
----------

As for finite differences, we compare the network with the analytical pressure
:eq:`eq-pression-analytique`, at test points that differ from the collocation
points.
