.. _sec-fd-cas-noye:

Finite differences: the shooting method
=======================================

The problem
-----------

On :math:`[X_{in}, X_{out}]`, with :math:`X_{in}` far upstream to approach
:math:`X_a = -\infty`:

.. math::

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   = \frac{\mathrm{d}H}{\mathrm{d}X} \ \text{on } [X_{in}, X_b],
   \qquad P = 0 \ \text{on } [X_b, X_{out}],

with :math:`P(X_{in}) = 0`. The boundary :math:`X_b` is unknown. It is set by
the Reynolds condition :math:`P(X_b) = \mathrm{d}P/\mathrm{d}X(X_b) = 0`.

The method
----------

The shooting method works like aiming a cannon: we guess the unknown, solve,
check whether a condition is met, then correct the guess.

- **What we do not know**: :math:`X_b`, where the film breaks up.
- **What we can already do**: for a guessed :math:`X_b`, the solver of
  :ref:`sec-fd-sans-cavitation` gives the pressure on :math:`[X_{in}, X_b]`
  with :math:`P = 0` at both ends.
- **The condition to check**: the slope at :math:`X_b` must also be zero. We
  compute it with a one-sided difference of order 2:

.. literalinclude:: /../src/fd/reynolds_1d_flooded.py
   :pyobject: outlet_slope

If the slope is negative, the pressure is still going down when it reaches
:math:`X_b`: the guess is too early. If it is positive, the pressure has gone
below zero and is coming back up: the guess is too late. Brent's method
(``scipy.optimize.root_scalar``) adjusts :math:`X_b` until the slope is zero.
Beyond :math:`X_b`, :math:`P = 0`.

This method is simple, but it only works in 1D with a single cavitated zone.
The general method with :math:`\theta` comes later.

Validation
----------

Since :math:`X_{in}` is finite, the case we solve is very slightly starved: it
is the analytical solution whose meniscus is at :math:`X_a = X_{in}`
(:ref:`sec-solution-analytique`). We compare :math:`X_b`, the load :math:`W`
and the pressure with this solution. When :math:`X_{in}` moves further away,
it tends to the flooded case.
