.. _sec-solution-analytique:

The 1D analytical solution
==========================

In 1D, the problem of :ref:`sec-equations` has an **exact** solution, given by
:cite:t:`biboulet2020hdr` (section 2.2.1). It will be the **reference** to
validate the finite difference method and then the PINN. Before we compare the
two methods with each other, each one must find this solution.

Idea: integrate the Reynolds equation once
------------------------------------------

In the pressurised zone, :math:`X_a < X < X_b`, the film is full
(:math:`\theta = 0`) and the constant flow rate :eq:`eq-debit-constant` reads
:math:`H - H^3 \, \mathrm{d}P/\mathrm{d}X = H_b`. So we know the pressure
gradient explicitly:

.. math::
   :label: eq-gradient-pression

   \frac{\mathrm{d}P}{\mathrm{d}X} = \frac{H - H_b}{H^3} .

This formula is easy to read:

- where :math:`H > H_b`, that is, upstream of :math:`-X_b`, the pressure
  **rises**: the oil dragged into the narrowing gap is squeezed;
- where :math:`H < H_b`, between :math:`-X_b` and :math:`X_b`, the pressure
  **falls**;
- so the pressure is **highest** at :math:`-X_b`, and the gradient is **zero
  again at** :math:`X_b`, where :math:`H(X_b) = H_b`. This is called the
  Reynolds condition at the cavitation boundary: the pressure reaches zero
  "smoothly", with a horizontal tangent.

Since :math:`H(X) = 1 + X^2/2`, the condition :math:`H(X_b) = H_b` gives the
position of the cavitation boundary:

.. math::
   :label: eq-xb

   X_b = \sqrt{2\, (H_b - 1)} .

The pressure
------------

We still have to integrate :eq:`eq-gradient-pression`. The calculation is
simpler with the auxiliary variable :math:`Y = X / \sqrt{2}`, for which
:math:`H = 1 + Y^2`. With :math:`Z = Y / H`, an antiderivative of the pressure
gradient is

.. math::
   :label: eq-primitive-pression

   P_d(Y) = \sqrt{2} \left[
   \left( \frac{1}{2} - \frac{3 H_b}{8} \right) \big( \arctan Y + Z \big)
   - \frac{Z}{4} \frac{H_b}{H}
   \right] .

The pressure must be zero at :math:`X_b`, that is, at
:math:`Y_b = \sqrt{H_b - 1}`. So we subtract the value of the antiderivative at
this point:

.. math::
   :label: eq-pression-analytique

   P(X) = P_d\!\left( \tfrac{X}{\sqrt{2}} \right) - P_d(Y_b),
   \qquad X_a \leq X \leq X_b .

Outside :math:`[X_a, X_b]`, :math:`P = 0`.

The void fraction
-----------------

Outside the pressurised zone, :math:`P = 0`, and the constant flow rate
:eq:`eq-debit-constant` directly gives the void fraction:

.. math::
   :label: eq-theta-analytique

   \theta(X) =
   \begin{cases}
     1 - \dfrac{H_b}{H(X)} & \text{if } X < X_a \text{ or } X > X_b, \\[2mm]
     0 & \text{if } X_a \leq X \leq X_b .
   \end{cases}

This solution has two typical properties, which the numerical methods must
reproduce:

- at :math:`X_b`, :math:`H = H_b`, so :math:`\theta` is 0 on both sides: the
  void fraction is **continuous** at the cavitation boundary;
- at :math:`X_a`, :math:`\theta` jumps suddenly from :math:`1 - H_b / H(X_a)`
  to 0: the void fraction is **discontinuous** at the inlet meniscus, where the
  oil suddenly fills the gap between the surfaces. The pressure is continuous
  there, but its gradient is not zero.

The inlet meniscus and the amount of oil
----------------------------------------

The pressure :eq:`eq-pression-analytique` depends on the parameter
:math:`H_b`, equal to the amount of available oil :math:`H_{\text{oil}}`. The
inlet meniscus :math:`X_a` is the position **upstream** (:math:`X_a < 0`)
where the pressure becomes zero:

.. math::
   :label: eq-xa

   P(X_a) = 0 .

This equation has no explicit solution. We solve it with Newton's method,
using :eq:`eq-gradient-pression` as the derivative: about ten iterations are
enough to reach machine precision :cite:p:`biboulet2020hdr`.

We can also go the other way: impose :math:`X_a` and look for the matching
:math:`H_b`, again with Newton on :math:`P(X_a) = 0`.

The load
--------

We get the load by integrating the pressure. :cite:t:`biboulet2020hdr` gives an
antiderivative:

.. math::
   :label: eq-charge-analytique

   \frac{W_d(Y)}{2} =
   Y \left( \frac{1}{2} - \frac{3 H_b}{8} \right) \big( \arctan Y - \arctan Y_b \big)
   + \frac{H_b}{8 H}
   + Y_b\, Y \left( \frac{3}{8} - \frac{1}{4 H_b} \right),
   \qquad
   W = W_d(Y_b) - W_d(Y_a),

with :math:`Y_a = X_a / \sqrt{2}`.

The flooded case and the reference values
-----------------------------------------

When the amount of oil increases, the inlet meniscus moves upstream. In the
limit :math:`X_a \to -\infty`, the contact is **flooded**: the condition
:math:`P(-\infty) = 0` sets the largest possible value of :math:`H_b`. The
reference values given by :cite:t:`biboulet2020hdr` are:

.. list-table:: Reference values (flooded case)
   :header-rows: 1
   :widths: 50 50

   * - Quantity
     - Value
   * - Outlet thickness :math:`H_{b,ff}`
     - :math:`\approx 1.226`
   * - Load :math:`W_{ff}`
     - :math:`\approx 0.408`

For the starved case, the HDR gives the following link between the position
of the inlet meniscus and the outlet thickness:

.. list-table:: Link :math:`X_a \leftrightarrow H_b` (HDR, figure 2.3)
   :header-rows: 1

   * - :math:`X_a`
     - :math:`-\infty`
     - :math:`-3`
     - :math:`-2`
     - :math:`-1.5`
     - :math:`-1`
     - :math:`-0.75`
     - :math:`-0.5`
   * - :math:`H_b`
     - 1.226
     - 1.201
     - 1.169
     - 1.136
     - 1.085
     - 1.053
     - 1.028

These values give a first simple test for any code: find :math:`H_{b,ff}` and
:math:`W_{ff}`, then the table above.

How the solution will be used to validate the methods
-----------------------------------------------------

For a given amount of oil, the analytical solution gives :math:`P(X)`,
:math:`\theta(X)`, :math:`X_a`, :math:`X_b` and :math:`W`. For each numerical
method, we will measure:

- the **error on the pressure** and on the **void fraction**, at every point;
- the **error on the position of the boundaries** :math:`X_a` and :math:`X_b`;
- the **error on the load** :math:`W`.
