.. _sec-contact-lubrifie:

The lubricated contact
======================

The physical situation
----------------------

In a rolling bearing, between a piston and a cylinder, or in a gear, two parts
roll or slide on each other. In this study, at least one of the surfaces is
moving. To stop them from touching and wearing out, we put a lubricant between
them, here oil. If the motion is fast enough, the oil dragged along by the
surfaces forms a continuous **film** that separates them completely. This is
called **hydrodynamic lubrication**.

This film is extremely thin compared with the parts around it. In this
project, its thickness is along the :math:`y` direction. Yet it can carry large
loads. Here is how:

- near the contact, the gap between the two surfaces first **narrows**
  (converging part), then **widens** (diverging part);
- the moving surfaces **drag** the oil into the narrowing gap, like a conveyor
  belt;
- the oil is forced into a space that gets smaller, and it cannot flow away
  fast enough: its **pressure rises**. This extra pressure keeps the surfaces
  apart and carries the load.

.. note:: A simple picture

   This is the same effect as aquaplaning. A car driving fast on a wet road
   drags water under the tyre. The water cannot escape fast enough, so its
   pressure rises and lifts the tyre.

The geometry
------------

The 1D case: a roller contact
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We take the simplest situation: a flat surface and a curved surface of radius
:math:`R_x`, for example a roller on a track (nothing moves along the roller
axis). Near the closest point, the gap between the surfaces, called the **film
thickness**, is well approximated by a parabola:

.. math::
   :label: eq-geometrie-dimensionnelle

   h(x) = h_0 + \frac{x^2}{2 R_x},

where :math:`x` is the position along the direction of motion and :math:`h_0`
is the minimum thickness, reached at :math:`x = 0`. For :math:`x < 0`, the film
narrows (converging). For :math:`x > 0`, it widens (diverging).

The surfaces move with a mean velocity :math:`u_m`. This is the speed at which
the oil is dragged into the contact.

The 2D case: the elliptical contact
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 1D case assumes that the roller is infinitely long: nothing changes along
its axis. In reality, the surfaces are often curved in **both** directions,
like a ball or a crowned roller on a track. We then add the direction
:math:`z`, perpendicular to the motion, with a second radius of curvature
:math:`R_z`. The film thickness becomes a paraboloid
:cite:p:`biboulet2020hdr`:

.. math::
   :label: eq-geometrie-dimensionnelle-2d

   h(x, z) = h_0 + \frac{x^2}{2 R_x} + \frac{z^2}{2 R_z} .

The lines of equal thickness are **ellipses**: this is called an **elliptical
contact**. Its shape is set by the ratio of the radii

.. math::

   D = \frac{R_x}{R_z} .

- :math:`D = 1`: the two radii are equal and the contact is circular (a ball on
  a plane);
- :math:`D \to 0`: :math:`R_z` becomes infinite, the surface is no longer
  curved along :math:`z`, and we get back the **1D case** (line contact). So 1D
  is the limit of an infinitely wide contact.

The key physical difference is **side leakage**. In 2D, part of the oil
dragged into the contact escapes sideways, in the :math:`z` direction, instead
of going through the contact. The amount of oil is no longer the same at the
inlet and at the outlet. The pressurised zone becomes a region of the plane,
bounded by curved boundaries.

The general assumptions of the full problem
-------------------------------------------

The project uses the simplest regime, called **iso-viscous rigid** (IVR):

- **iso-viscous**: the oil viscosity :math:`\eta_0` is constant. In reality, it
  increases with pressure, but we neglect this effect;
- **rigid**: the surfaces do not deform under pressure. So the geometry
  :eq:`eq-geometrie-dimensionnelle` is known in advance and does not depend on
  the solution.

We add the classical assumptions of thin-film lubrication:

- the film is **thin** compared with the other dimensions of the contact;
- the oil is a **Newtonian** and **incompressible** fluid, and the flow is
  **laminar**: viscous forces dominate and inertia is negligible;
- the pressure is **constant across the thickness** of the film;
- the oil **sticks** to the walls (no slip at the wall);
- the regime is **steady** and **isothermal**;
- in 1D, the contact is **infinitely wide** in the direction perpendicular to
  the motion: the oil cannot escape sideways.

The two effects that make the problem harder
--------------------------------------------

Cavitation
~~~~~~~~~~

In the diverging part, the gap between the surfaces grows. There, the
equation that describes the film (:ref:`sec-equations`) predicts a **pressure
drop**. The pressure becomes **lower** than the ambient pressure, and the
solution can even be negative. A liquid cannot withstand such a drop: the film
**breaks up**, pockets of gas or vapour appear, and the oil no longer fills the
whole space between the surfaces. This is **cavitation**.

In a cavitated zone:

- the pressure stays equal to the **cavitation pressure**, which we take as the
  reference: :math:`p = 0`;
- the space between the surfaces is only **partly** filled with oil. We write
  :math:`\theta` for the **void fraction**: :math:`\theta = 0` if the film is
  full, :math:`\theta = 0.3` if gas fills 30 % of the thickness.

The boundary between the full zone and the cavitated zone is not known in
advance: it is part of the solution. It is a **free boundary**, and it is the
main numerical difficulty of the problem.

Limited oil supply
~~~~~~~~~~~~~~~~~~

The "ideal" case assumes there is plenty of oil in front of the contact: the
contact is called **flooded**. Often this is not true: the surfaces only bring
an **oil layer of finite thickness** :math:`h_{\text{oil}}`. The contact is
then **starved**.

The consequence: the film only becomes full from a certain position
:math:`x_a`, called the **inlet meniscus**. This is where the gap between the
surfaces becomes equal to the available oil thickness. Upstream of it, the
space is partly empty. The less oil there is, the closer the inlet meniscus
moves to the centre of the contact, the smaller the pressurised zone, and the
lower the load the contact can carry.

What we are looking for
-----------------------

So the contact has three zones, from upstream to downstream:

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Zone
     - Film
     - Pressure
     - Void fraction
   * - before the inlet meniscus :math:`x_a`
     - partly filled
     - :math:`p = 0`
     - :math:`\theta > 0`
   * - between :math:`x_a` and :math:`x_b`
     - full
     - :math:`p > 0`
     - :math:`\theta = 0`
   * - after the cavitation boundary :math:`x_b`
     - partly filled (cavitation)
     - :math:`p = 0`
     - :math:`\theta > 0`

Solving the problem means finding, for a given amount of available oil, the
**pressure** :math:`p(x)` and the **void fraction** :math:`\theta(x)` at every
point.

Then we can compute:

- the positions of the two boundaries: the **inlet meniscus** :math:`x_a` and
  the **cavitation boundary** :math:`x_b`;
- the **load** :math:`w` the contact can carry, equal to the integral of the
  pressure.
