.. _sec-equations:

The equations to solve
======================

Where the Reynolds equation comes from
--------------------------------------

The Reynolds equation expresses a simple idea: **oil does not disappear**. In
steady state and in 1D, the oil flow rate through each cross-section of the
film is the same everywhere. This is the classical conservation of flow rate
:math:`\mathrm{d}q / \mathrm{d}x = 0` from fluid mechanics.

Across the film thickness, the oil velocity is the sum of two flows:

- a **Couette** flow, caused by the surfaces dragging the oil. It carries the
  oil at the mean velocity :math:`u_m`;
- a **Poiseuille** flow, caused by the pressure gradient. The oil is pushed
  from high-pressure zones towards low-pressure zones.

We integrate the velocity profile over the thickness :math:`h` (the :math:`y`
direction). The flow rate per unit width is

.. math::
   :label: eq-debit-dimensionnel

   q = \underbrace{u_m\, h}_{\text{Couette}}
     \; \underbrace{- \, \frac{h^3}{12\,\eta_0} \frac{\mathrm{d}p}{\mathrm{d}x}}_{\text{Poiseuille}} .

Writing that this flow rate is constant, :math:`\mathrm{d}q / \mathrm{d}x = 0`,
gives the **Reynolds equation** for a full film, in the iso-viscous rigid
regime:

.. math::
   :label: eq-reynolds-dimensionnelle

   \frac{\mathrm{d}}{\mathrm{d}x} \left( h^3 \frac{\mathrm{d}p}{\mathrm{d}x} \right)
   = 12\, \eta_0\, u_m \frac{\mathrm{d}h}{\mathrm{d}x} .

The right-hand side shows what creates the pressure: the **change in
thickness**, :math:`\mathrm{d}h / \mathrm{d}x`, combined with the drag
:math:`u_m`. If the surfaces were parallel, there would be no extra pressure.

Dimensionless form
------------------

The physical quantities have very different sizes: micrometres for :math:`h`,
millimetres for :math:`x`, megapascals for :math:`p`. We replace them with
**dimensionless** quantities of order 1. This makes the equations simpler and
suits numerical computation better:

.. math::
   :label: eq-adimensionnement

   X = \frac{x}{\sqrt{R_x h_0}}, \qquad
   H = \frac{h}{h_0}, \qquad
   P = \frac{p\, h_0^{3/2}}{12\, \eta_0\, u_m\, R_x^{1/2}}, \qquad
   W = \frac{w\, h_0}{12\, \eta_0\, u_m\, R_x} .

With these variables, the geometry :eq:`eq-geometrie-dimensionnelle` and the
Reynolds equation :eq:`eq-reynolds-dimensionnelle` become

.. math::
   :label: eq-geometrie

   H(X) = 1 + \frac{X^2}{2},

.. math::
   :label: eq-reynolds

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   = \frac{\mathrm{d}H}{\mathrm{d}X} .

.. note:: A problem with no parameter

   These variables have a remarkable advantage: the radius :math:`R_x`, the
   viscosity :math:`\eta_0`, the velocity :math:`u_m` and the thickness
   :math:`h_0` have all disappeared. For a parabolic contact, there is only
   **one** equation to solve, whatever the real contact. The only parameter
   left is the amount of available oil (see below). Physical units are only
   used for the final display.

From now on, **all quantities are dimensionless**.

Taking cavitation into account: complementarity
-----------------------------------------------

The conservative Reynolds equation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Equation :eq:`eq-reynolds` is only valid where the film is full. To describe
the **whole** contact, including the cavitated zones, we write the flow rate
balance again, this time with the void fraction :math:`\theta`. Only the part
filled with oil, :math:`(1 - \theta) H`, is dragged by the surfaces. The
dimensionless flow rate is

.. math::
   :label: eq-debit

   Q = (1 - \theta)\, H - H^3 \frac{\mathrm{d}P}{\mathrm{d}X} .

Its conservation, :math:`\mathrm{d}Q / \mathrm{d}X = 0`, gives the
**conservative** Reynolds equation (it conserves the mass of oil, including in
the cavitated zones) :cite:p:`biboulet2020hdr`:

.. math::
   :label: eq-reynolds-theta

   \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
   - \frac{\mathrm{d}}{\mathrm{d}X} \Big( (1 - \theta)\, H \Big) = 0 .

We check that it gives the two expected behaviours:

- **full film** (:math:`\theta = 0`): we get exactly :eq:`eq-reynolds`;
- **cavitated zone** (:math:`P = 0`): what is left is
  :math:`\mathrm{d}\big((1-\theta) H\big)/\mathrm{d}X = 0`. The amount of oil
  :math:`(1 - \theta) H` is simply carried along, with no pressure.

The complementarity condition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One equation is missing: we have two unknowns, :math:`P` and :math:`\theta`,
but only one equation. The second equation says that, at each point, **only
one of two situations** is possible:

- either the film is full: :math:`\theta = 0` and :math:`P \geq 0`;
- or it is partial: :math:`P = 0` and :math:`\theta \geq 0`.

The pressure cannot be negative (the film would break up). Neither can the
void fraction. And both cannot be positive at the same time. These three
conditions form a **complementarity condition**:

.. math::
   :label: eq-complementarite

   P \geq 0, \qquad \theta \geq 0, \qquad P\, \theta = 0 .

This condition is easy to understand physically, but hard to use numerically:
it is two inequalities and one equality. We replace it with **a single
equation**, using the **Fischer-Burmeister** function
:cite:p:`biboulet2020hdr`:

.. math::
   :label: eq-fischer-burmeister

   \phi(P, \theta) = P + \theta - \sqrt{P^2 + \theta^2} = 0 .

.. note:: Why :math:`\phi = 0` is the same as complementarity

   If :math:`\phi = 0`, then :math:`P + \theta = \sqrt{P^2 + \theta^2} \geq 0`.
   Squaring both sides: :math:`P^2 + 2 P \theta + \theta^2 = P^2 + \theta^2`,
   so :math:`P \theta = 0`. One of the two quantities is zero. The other one is
   then equal to its own absolute value: it is positive or zero. Conversely, if
   :eq:`eq-complementarite` holds, we can check directly that :math:`\phi = 0`.

So the system to solve has **two equations for two unknowns**,
:eq:`eq-reynolds-theta` and :eq:`eq-fischer-burmeister`. This is a big
advantage: we do not have to look for the boundaries :math:`X_a` and
:math:`X_b` separately. They appear by themselves in the solution, where we go
from :math:`\theta > 0` to :math:`P > 0`.

Limited oil supply
------------------

We write :math:`H_{\text{oil}} = h_{\text{oil}} / h_0` for the dimensionless
thickness of the oil layer brought by the surfaces. Upstream of the contact,
this oil is simply carried along, so the flow rate is
:math:`Q = H_{\text{oil}}`.

In 1D, the oil cannot escape sideways, so the flow rate is **the same in the
whole contact**:

.. math::
   :label: eq-debit-constant

   Q = (1 - \theta)\, H - H^3 \frac{\mathrm{d}P}{\mathrm{d}X} = H_{\text{oil}}
   \quad \text{everywhere.}

Two consequences:

- at the outlet, beyond the cavitation boundary, :math:`P = 0`, so
  :math:`(1 - \theta) H = H_{\text{oil}}`: **all the oil that went in comes
  out**. In particular, at the point :math:`X_b`, the film is still full and
  the pressure gradient is zero. So the film thickness there is
  :math:`H_b = H(X_b) = H_{\text{oil}}`;
- the amount of available oil is **the only parameter** of the problem. We can
  give it equally well with :math:`H_{\text{oil}}`, with :math:`H_b`, or with
  the position of the inlet meniscus :math:`X_a`.

A contact can only let a limited amount of oil through. Above a threshold,
written :math:`H_{b,ff}` (*fully flooded*, see
:ref:`sec-solution-analytique`), the contact is **flooded**: the inlet meniscus
moves infinitely far upstream, and extra oil no longer changes the solution.

The full problem
----------------

.. admonition:: Problem to solve (1D)

   **Data**: the geometry :math:`H(X) = 1 + X^2/2`, a domain
   :math:`[X_{\text{in}}, X_{\text{out}}]`, and the amount of available oil
   :math:`H_{\text{oil}}`.

   **Unknowns**: the pressure :math:`P(X)` and the void fraction
   :math:`\theta(X)`.

   **Equations**, at every point of the domain:

   .. math::

      \frac{\mathrm{d}}{\mathrm{d}X} \left( H^3 \frac{\mathrm{d}P}{\mathrm{d}X} \right)
      - \frac{\mathrm{d}}{\mathrm{d}X} \Big( (1 - \theta)\, H \Big) = 0,
      \qquad
      P + \theta - \sqrt{P^2 + \theta^2} = 0 .

   **Boundary conditions**:

   .. math::

      P(X_{\text{in}}) = 0, \qquad P(X_{\text{out}}) = 0, \qquad
      \theta(X_{\text{in}}) = 1 - \frac{H_{\text{oil}}}{H(X_{\text{in}})} .

   The last condition says that, at the domain inlet, the gap
   :math:`H(X_{\text{in}})` only contains the oil layer :math:`H_{\text{oil}}`.

   **Quantities to get**: :math:`P(X)`, :math:`\theta(X)`, the inlet meniscus
   :math:`X_a`, the cavitation boundary :math:`X_b`, and the load

   .. math::

      W = \int_{X_a}^{X_b} P(X)\, \mathrm{d}X .

The domain must be large enough to contain the whole pressurised zone:
:math:`X_{\text{in}} < X_a` and :math:`X_{\text{out}} > X_b`.

The 2D extension
----------------

For the elliptical contact :eq:`eq-geometrie-dimensionnelle-2d`, the
transverse direction is made dimensionless with its own radius,
:math:`Z = z / \sqrt{R_z h_0}`, and the pressure as in 1D. The geometry becomes
:cite:p:`biboulet2020hdr`

.. math::
   :label: eq-geometrie-2d

   H(X, Z) = 1 + \frac{X^2}{2} + \frac{Z^2}{2},

and the Reynolds equation for a full film takes the form (eq. 2.30 of the HDR)

.. math::
   :label: eq-reynolds-2d

   \frac{\partial}{\partial X} \left( H^3 \frac{\partial P}{\partial X} \right)
   + D\, \frac{\partial}{\partial Z} \left( H^3 \frac{\partial P}{\partial Z} \right)
   = \frac{\partial H}{\partial X} .

The new term describes the Poiseuille flow in the :math:`Z` direction, that
is, the **side leakage**. The ratio of the radii :math:`D` is the only
geometric parameter left: for :math:`D = 0`, we get back the 1D equation
:eq:`eq-reynolds`. There is no Couette term along :math:`Z`, because the
surfaces only move along :math:`X`.

Cavitation is handled as in 1D: only the filled part :math:`(1 - \theta) H` is
dragged along. This gives the conservative equation

.. math::
   :label: eq-reynolds-theta-2d

   \frac{\partial}{\partial X} \left( H^3 \frac{\partial P}{\partial X} \right)
   + D\, \frac{\partial}{\partial Z} \left( H^3 \frac{\partial P}{\partial Z} \right)
   - \frac{\partial}{\partial X} \Big( (1 - \theta)\, H \Big) = 0,

with the same Fischer-Burmeister condition. The HDR writes this equation
(eq. 3.51) for textured surfaces, with both directions made dimensionless in
the same way, which amounts to :math:`D = 1`. The cavitation boundary becomes
a curve in the plane. The flow rate is no longer constant (part of the oil
leaves sideways), and there is no exact analytical solution any more. There is
only a quasi-analytical solution for wide elliptical contacts (section 2.2.2
of :cite:t:`biboulet2020hdr`).
