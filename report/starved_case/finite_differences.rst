.. _sec-fd-starved:

Finite differences: the combined unknown u = P − θ
==================================================

The problem
-----------

We solve the conservative Reynolds equation :eq:`eq-reynolds-theta` with the
complementarity condition :eq:`eq-complementarite`, on
:math:`[X_{in}, X_{out}]`. At the inlet, :math:`P = 0` and only the oil layer
comes in: :math:`\theta = 1 - H_{\text{oil}} / H(X_{in})`. At the outlet,
:math:`P = 0`.

The key idea: one unknown instead of two
----------------------------------------

At each point, we have two unknowns, :math:`P` and :math:`\theta`, and we know
that **one of them is always zero**. :cite:t:`biboulet2020hdr` (section 3.3.3)
uses this to replace them with a single unknown:

.. math::

   u = P - \theta .

We can always get :math:`P` and :math:`\theta` back from :math:`u`:

- if :math:`u > 0`, the point is in the full film: :math:`P = u` and
  :math:`\theta = 0`;
- if :math:`u < 0`, the point is cavitated: :math:`P = 0` and
  :math:`\theta = -u`.

In other words, :math:`P` is the positive part of :math:`u`, and
:math:`\theta` is its negative part. A single curve :math:`u(X)` shows the
whole solution: above zero we read the pressure, below zero we read the void
fraction.

.. literalinclude:: /../src/fd/reynolds_1d_starved.py
   :pyobject: pressure_and_void_fraction

.. note:: Why this is a clever idea

   The usual approach, following Woloszynski et al. (cited in the HDR), solves
   two equations for two unknowns: Reynolds and Fischer-Burmeister
   :eq:`eq-fischer-burmeister`. The combined unknown, proposed by
   :cite:t:`biboulet2020hdr`, makes this much simpler:

   - **complementarity holds automatically**: :math:`P` and :math:`\theta`
     built from :math:`u` are never negative and never positive at the same
     time. The Fischer-Burmeister equation is always satisfied, so only the
     Reynolds equation is left, with **one equation per point**;
   - **no switching**: we never have to decide in advance which points are
     full and which are cavitated. The sign of :math:`u` says it;
   - **the unknown is almost continuous**: :math:`u` goes smoothly from
     positive to negative at :math:`X_b`, which helps the solver.

   In the HDR, the whole solver fits in about forty lines of Matlab.

The discretisation
------------------

The grid has :math:`n` evenly spaced points. The Reynolds equation becomes, at
each point :math:`i`,

.. math::

   r_i = (A_P\, P)_i + (A_\theta\, \theta)_i - \left(\frac{\mathrm{d}H}{\mathrm{d}X}\right)_i = 0 .

- :math:`A_P` is the Poiseuille term :math:`\mathrm{d}/\mathrm{d}X(H^3\,\mathrm{d}P/\mathrm{d}X)`,
  written in conservative form, with :math:`H^3` taken halfway between two
  points.
- :math:`A_\theta` is the derivative of :math:`\theta H`. It uses an **upwind**
  formula: the oil, and the gas with it, is carried from left to right, so the
  derivative at point :math:`i` uses point :math:`i` and the points on its
  left.

These matrices only depend on the geometry, so we build them once.

Newton's method
---------------

The equation is not linear in :math:`u`, because of the positive and negative
parts. We solve it with Newton's method. At each step, we ask: "if I change
:math:`u_k` a little, what changes?"

- at a full-film point (:math:`u_k > 0`), changing :math:`u_k` changes the
  pressure, so the column :math:`k` of :math:`A_P` counts;
- at a cavitated point (:math:`u_k < 0`), changing :math:`u_k` changes the void
  fraction (with a minus sign), so the column :math:`k` of :math:`A_\theta`
  counts.

This gives the matrix of the Newton step (HDR, eq. 3.61), :math:`J = A_P C_\theta - A_\theta C_P`,
where :math:`C_\theta` keeps the full-film columns and :math:`C_P` keeps the
cavitated ones. We solve :math:`J \delta = -r` and update :math:`u`. We stop
when the residual is tiny.

.. literalinclude:: /../src/fd/reynolds_1d_starved.py
   :pyobject: newton_solve

Two practical choices
---------------------

- **The first guess**: no pressure anywhere, and the oil simply carried along
  (:math:`\theta = 1 - H_{\text{oil}}/H`). If we start with a positive pressure
  everywhere instead, Newton finds a wrong solution, where the meniscus sticks
  to the inlet.
- **Grid refinement** :cite:p:`biboulet2020hdr`: we first solve on a coarse
  grid, then use the result as the first guess on a grid twice as fine, and so
  on. On each level, the boundaries only move a little, so Newton needs only a
  few steps.

Validation
----------

We compare the solver with the analytical solution
(:ref:`sec-solution-analytique`) for three amounts of oil, from very little
oil to an almost flooded contact. Both solutions are evaluated on the same
grid. We check four things:

- **the pressure** :math:`P`, at every point;
- **the load** :math:`W`, the integral of the pressure;
- **the two boundaries**: :math:`X_a` is the first point with :math:`P > 0`,
  and :math:`X_b` is the last one. A boundary always falls between two grid
  points, so we accept an error of two grid cells;
- **the void fraction** :math:`\theta`, away from the meniscus. :math:`\theta`
  jumps at :math:`X_a`: a meniscus one grid cell off gives a large error at
  that single point, which says nothing about the quality of the solution. So
  we leave out the points close to :math:`X_a`.
