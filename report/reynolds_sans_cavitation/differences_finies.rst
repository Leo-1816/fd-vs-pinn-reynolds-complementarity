.. _sec-fd-sans-cavitation:

Finite differences
==================

The problem
-----------

We solve the Reynolds equation :eq:`eq-reynolds` on an interval
:math:`[X_{in}, X_{out}]`, with zero pressure at both ends:

.. math::

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   = \frac{\mathrm{d}H}{\mathrm{d}X},
   \qquad P(X_{in}) = P(X_{out}) = 0 .

We assume the film is full everywhere (:math:`\theta = 0`), so :math:`P` is
the only unknown.

The discretisation
------------------

We expand the derivative:

.. math::

   H^3 P'' + 3 H^2 H' P' = H', \qquad H' = X .

We cut the domain into :math:`n` evenly spaced points :math:`X_i`, a distance
:math:`\Delta X` apart. At each interior point, we replace the derivatives by
centred differences:

.. math::

   P'' \approx \frac{P_{i-1} - 2 P_i + P_{i+1}}{\Delta X^2}, \qquad
   P' \approx \frac{P_{i+1} - P_{i-1}}{2 \Delta X} .

So each interior point gives one linear equation that links
:math:`P_{i-1}`, :math:`P_i` and :math:`P_{i+1}`. The two ends give
:math:`P_0 = 0` and :math:`P_{n-1} = 0`. We get a system :math:`A P = b`, where
:math:`A` is tridiagonal (only three non-zero diagonals). We solve it directly,
in double precision.

.. literalinclude:: /../src/fd/reynolds_1d.py
   :pyobject: solve
